# pyright: ignore
# type: ignore

"""
FastAPI REST API Servisi
=========================
AI Phishing tespit modelimizi bir web servisi (API) olarak dışa açar.
Chrome eklentileri veya web frontend'leri bu API üzerinden analiz yapabilir.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
import uvicorn
from typing import List, Optional

from crawler.web_crawler import crawl_site
from features.url_features import extract_url_features
from features.text_features import extract_text_features
from model.ml_model import predict_phishing

# ---------------------------------------------------------------------------
# 📦 Veri Modelleri (Pydantic ile Doğrulama)
# ---------------------------------------------------------------------------
class AnalyzeRequest(BaseModel):
    url: HttpUrl

class AnalyzeResponse(BaseModel):
    url: str
    status: str
    label: str
    confidence: float
    risk_score: int
    risk_level: str
    suspicious_features: List[str]
    features: Optional[dict] = None
    error: Optional[str] = None

# ---------------------------------------------------------------------------
# 🚀 API Uygulaması
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Phishing Detection API",
    description="URL ve içerik tabanlı AI phishing tespit sistemi",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend klasörünü serve et
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_url(request: AnalyzeRequest):
    """
    Verilen URL'yi tarar, NLP ve ML motorunu kullanarak risk analizi yapar.
    """
    url_str = str(request.url)
    
    try:
        # 1. Crawler
        try:
            page_text, links, html = crawl_site(url_str)
        except Exception as e:
            print(f"[API] Crawler Hatası: {e}")
            page_text, html = "", ""
            
        # 2. URL Özellikleri
        url_feats = extract_url_features(url_str)
        
        # 3. Text & HTML Özellikleri
        text_feats = extract_text_features(page_text, html)
        
        # 4. Feature Vector Birleştirme
        feature_vector = {}
        feature_vector.update(url_feats)
        feature_vector.update(text_feats)
        
        # 5. ML Tahmini
        result = predict_phishing(feature_vector)
        
        return AnalyzeResponse(
            url=url_str,
            status="success",
            label=result["label"].upper(),
            confidence=result["confidence"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            suspicious_features=result["suspicious_features"],
            features=feature_vector
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz sırasında hata oluştu: {str(e)}")

if __name__ == "__main__":
    print("\n[🚀] API Başlatılıyor... http://127.0.0.1:8000/docs adresinden test edebilirsiniz.")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

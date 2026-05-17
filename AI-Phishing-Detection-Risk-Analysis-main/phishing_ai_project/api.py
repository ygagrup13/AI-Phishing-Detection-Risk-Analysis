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

from crawler.web_crawler import crawl_site, crawl_with_cloudflare
from features.url_features import extract_url_features
from features.text_features import extract_text_features
from model.ml_model import predict_phishing

USE_CLOUDFLARE = True  # Cloudflare API anahtarı varsa True yap

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
    warning: Optional[str] = None
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

SAFE_DOMAINS = [
    'youtube.com', 'youtu.be', 'google.com', 'gmail.com',
    'facebook.com', 'instagram.com', 'twitter.com', 'x.com',
    'linkedin.com', 'microsoft.com', 'apple.com', 'amazon.com',
    'netflix.com', 'spotify.com', 'github.com', 'stackoverflow.com',
    'wikipedia.org', 'reddit.com', 'twitch.tv', 'discord.com',
    'trendyol.com', 'hepsiburada.com', 'sahibinden.com',
    'ziraat.com.tr', 'garantibbva.com.tr', 'akbank.com',
    'isbank.com.tr', 'vakifbank.com.tr',
    'firat.edu.tr', 'edu.tr', 'gov.tr', 'com.tr', 'org.tr',
    'meb.gov.tr', 'yok.gov.tr', 'tubitak.gov.tr',
    'itu.edu.tr', 'metu.edu.tr', 'boun.edu.tr', 'hacettepe.edu.tr',
    'ankara.edu.tr', 'istanbul.edu.tr', 'ege.edu.tr',
    'obs.firat.edu.tr', 'debsis.firat.edu.tr', 'jasig.firat.edu.tr',
]

from urllib.parse import urlparse, parse_qs

def is_safe_redirect(url: str) -> bool:
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        service = params.get('service', [''])[0]
        if service:
            service_host = urlparse(service).hostname or ""
            if service_host.endswith('.edu.tr') or service_host.endswith('.gov.tr'):
                return True
    except:
        pass
    return False

def is_known_safe_domain(url: str) -> bool:
    try:
        from urllib.parse import urlparse
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        hostname = urlparse(url).hostname or ""
        hostname = hostname.replace('www.', '').lower()
        
        if is_safe_redirect(url):
            return True
        
        if not any(hostname == d or hostname.endswith('.' + d) for d in SAFE_DOMAINS):
            return False
            
        # YouTube özel kontrolü: Video gerçekten var mı? (YouTube 404 yerine 200 döndürebilir)
        if 'youtube.com' in hostname or 'youtu.be' in hostname:
            oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
            oembed_response = requests.get(oembed_url, timeout=5, verify=False)
            if oembed_response.status_code != 200:
                return False
            return True
            
        # Domain güvenli ama URL erişilebilir mi kontrol et
        response = requests.head(url, timeout=5, allow_redirects=True, verify=False)
        # 404 veya erişim yoksa safe domain muamelesi yapma
        if response.status_code in [404, 410, 400]:
            return False
        return True
    except:
        return False

NOT_FOUND_SIGNALS = [
    '404', 'not found', 'page not found', 'sayfa bulunamadı',
    'bu sayfa mevcut değil', 'video unavailable', 'video is unavailable',
    'this page doesn\'t exist', 'bu video mevcut değil'
]

def is_page_not_found(page_text: str) -> bool:
    text_lower = page_text.lower()
    return any(signal in text_lower for signal in NOT_FOUND_SIGNALS)

def validate_url(url: str) -> tuple:
    """URL format kontrolü — sadece yapısal doğrulama, ağ isteği yok."""
    try:
        parsed = urlparse(url)

        # Protokol kontrolü
        if parsed.scheme not in ['http', 'https']:
            return False, "Geçersiz protokol. URL http:// veya https:// ile başlamalı."

        # Domain kontrolü
        hostname = parsed.hostname or ""
        if not hostname or len(hostname) < 3:
            return False, "Geçersiz domain adı."

        # En az bir nokta olmalı
        if '.' not in hostname:
            return False, "Geçersiz domain. En az bir nokta içermeli."

        # Domain kısmında boşluk olmamalı
        if ' ' in hostname:
            return False, "Domain adında boşluk olamaz."

        # TLD en az 2 karakter olmalı
        tld = hostname.split('.')[-1]
        if len(tld) < 2:
            return False, "Geçersiz domain uzantısı."

        return True, None

    except Exception as e:
        return False, f"URL ayrıştırma hatası: {str(e)}"

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_url(request: AnalyzeRequest):
    """
    Verilen URL'yi tarar, NLP ve ML motorunu kullanarak risk analizi yapar.
    """
    url_str = str(request.url)

    # --- URL Geçerlilik Kontrolü ---
    is_valid, url_warning = validate_url(url_str)
    if not is_valid:
        return {
            "url": url_str,
            "status": "error",
            "label": "GEÇERSİZ URL",
            "confidence": 0.0,
            "risk_score": 0,
            "risk_level": "Bilinmiyor",
            "suspicious_features": [],
            "warning": url_warning,
            "error": url_warning
        }
    
    if is_known_safe_domain(url_str):
        return {
            "url": url_str,
            "status": "success",
            "label": "LEGITIMATE",
            "confidence": 0.99,
            "risk_score": 5,
            "risk_level": "Düşük",
            "suspicious_features": [],
            "warning": None,
            "error": None
        }
    
    try:
        # 1. Crawler
        try:
            if USE_CLOUDFLARE:
                page_text, links, html = crawl_with_cloudflare(url_str)
            else:
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
        feature_vector["_url"] = url_str
        
        # 5. ML Tahmini
        result = predict_phishing(feature_vector)

        # Crawler'dan dönen metin boşsa site erişilemez demektir
        site_accessible = bool(page_text and len(page_text.strip()) > 50)

        # Typosquatting varsa site erişilemez olsa bile PHISHING kal — override etme
        has_typosquatting = 'typosquatting' in result.get('suspicious_features', [])
        has_taklit_warning = any(
            word in str(result.get('warning', '')).lower()
            for word in ['taklit', 'typosquat', 'marka', 'similar']
        )

        if has_typosquatting or has_taklit_warning:
            # Typosquatting tespit edildi — label değişmesin, sadece erişim notu ekle
            if not site_accessible:
                result['warning'] = str(result.get('warning', '')) + " (Site erişilemez durumda)"
        elif not site_accessible:
            if result['label'] == 'PHISHING':
                result['warning'] = "⚠️ Bu siteye erişilemedi ancak URL yapısı phishing belirtileri taşıyor."
                result['confidence'] = round(result['confidence'] * 0.8, 2)
            else:
                result['label'] = 'BELİRSİZ'
                result['warning'] = "⚠️ Bu siteye erişilemedi. URL yapısı temiz görünüyor ancak doğrulanamadı."
                result['risk_score'] = min(result['risk_score'], 30)
                result['risk_level'] = 'Düşük'
        elif is_page_not_found(page_text):
            result["warning"] = "⚠️ Bu sayfa mevcut değil veya erişilemiyor. URL geçersiz olabilir."

        # validate_url'den gelen uyarıyı yalnızca başka warning yoksa ekle
        if url_warning and not result.get("warning"):
            result["warning"] = url_warning

        return AnalyzeResponse(
            url=url_str,
            status="success",
            label=result["label"].upper(),
            confidence=result["confidence"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            suspicious_features=result["suspicious_features"],
            features=feature_vector,
            warning=result.get("warning")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz sırasında hata oluştu: {str(e)}")

if __name__ == "__main__":
    print("\n[🚀] API Başlatılıyor... http://127.0.0.1:8000/docs adresinden test edebilirsiniz.")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

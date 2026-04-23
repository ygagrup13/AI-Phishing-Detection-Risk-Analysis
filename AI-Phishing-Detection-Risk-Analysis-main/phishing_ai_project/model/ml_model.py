# pyright: ignore
# type: ignore

"""
Makine Öğrenmesi Modülü (ML Model)
====================================
Sorumlu : Meryem
Açıklama:
    Model SADECE URL feature'ları kullanılarak eğitilir. 
    (Çünkü NLP özellikleri dataset'te çoğunlukla 0 geldiğinden model NLP'yi göz ardı ediyor).
    Bunun yerine, TEXT/HTML özellikleri tahmin sonrasında KURAL TABANLI olarak risk_score'a yansıtılır.
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import joblib

# Python modül yollarını çözmek için
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from features.url_features import URL_FEATURE_KEYS, extract_url_features

warnings.filterwarnings("ignore")

# Modelin kullanacağı sadece URL Feature'ları
FEATURE_COLUMNS = list(URL_FEATURE_KEYS)

DATASET_PATH = os.path.join(BASE_DIR, "data", "crawled_texts", "dataset_phishing.csv")
MODEL_PATH = os.path.join(BASE_DIR, "data", "rf_model.pkl")

_SUSPICIOUS_THRESHOLDS = {
    "has_https":                   ("==", 0),
    "has_at":                      ("==", 1),
    "dash_count":                  (">=", 3),
    "has_ip":                      ("==", 1),
    "subdomain_count":             (">=", 2),
    "suspicious_keyword_count":    (">=", 2),
    "is_suspicious_tld":           ("==", 1),
    "has_double_extension":        ("==", 1),
    "phishing_lexicon_mention_count": (">=", 3),
    "phishing_text_risk_0_100":    (">=", 40),
    "form_count":                  (">=", 2),
    "hidden_element_count":        (">=", 1),
    "favicon_foreign":             ("==", 1),
    "external_link_ratio":         (">=", 0.5),
}

def train_and_save_model():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"[HATA] Dataset bulunamadı: {DATASET_PATH}")
        
    print(f"[ML MODEL] Gerçek dataset yükleniyor: {DATASET_PATH}")
    df_raw = pd.read_csv(DATASET_PATH)
    
    print("[ML MODEL] Ham URL'lerden Feature Extraction yapılıyor (Bu işlem 3-5 saniye sürebilir)...")
    
    def safe_extract(url_val):
        try:
            return extract_url_features(str(url_val))
        except:
            return {k: 0 for k in FEATURE_COLUMNS}
            
    # Tüm dataset üzerindeki 'url' kolonundan kendi yazdığımız 20 özelliği (URL_FEATURE_KEYS) çıkartıyoruz.
    # Böylece model tam olarak bizim özelliklerimizin ağırlığını öğrenecek.
    extracted_features = df_raw["url"].apply(safe_extract).tolist()
    df_features = pd.DataFrame(extracted_features)[FEATURE_COLUMNS]
            
    y = df_raw["status"].apply(lambda x: 1 if str(x).strip().lower() == "phishing" else 0)
    
    print("[ML MODEL] Sadece URL feature'ları ile RandomForest eğitiliyor...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=20, min_samples_leaf=1)
    
    scores = cross_val_score(rf, df_features, y, cv=3, scoring="f1")
    print(f"[ML MODEL] F1 Skoru (Sadece URL): {scores.mean():.4f} (±{scores.std():.4f})")
    
    rf.fit(df_features, y)
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(rf, MODEL_PATH)
    print(f"[ML MODEL] Eğitim tamamlandı ve kaydedildi: {MODEL_PATH}\n")
    return rf

_global_model = None

def _get_model():
    global _global_model
    if _global_model is None:
        if os.path.exists(MODEL_PATH):
            _global_model = joblib.load(MODEL_PATH)
        else:
            print("[ML MODEL] Model dosyası bulunamadı, sıfırdan eğitiliyor...")
            _global_model = train_and_save_model()
    return _global_model

def _detect_suspicious(feature_vector: dict) -> list:
    suspicious = []
    for feat, (op, threshold) in _SUSPICIOUS_THRESHOLDS.items():
        val = feature_vector.get(feat, 0)
        try:
            val = float(val)
            if op == ">"  and val >  threshold:
                suspicious.append(feat)
            elif op == ">=" and val >= threshold:
                suspicious.append(feat)
            elif op == "==" and val == threshold:
                suspicious.append(feat)
        except (TypeError, ValueError):
            pass
    return suspicious

def predict_phishing(feature_vector: dict) -> dict:
    model = _get_model()
    
    # Modele sadece eğitildiği URL featurelarını gönder
    ordered = {col: float(feature_vector.get(col, 0)) for col in FEATURE_COLUMNS}
    X = pd.DataFrame([ordered])

    try:
        proba = float(model.predict_proba(X)[0][1])  # P(phishing)
    except Exception as exc:
        print(f"[ML MODEL] Tahmin hatası: {exc}")
        proba = 0.0

    confidence  = round(proba, 4)
    risk_score  = int(round(confidence * 100))

    # NLP Özelliklerini Kural Tabanlı olarak risk_score'a ekle (Ceza puanları)
    tfidf_score = feature_vector.get("phishing_tfidf_weighted_score", 0.0)
    if float(tfidf_score) > 1.5:
        risk_score += 15

    form_cnt = feature_vector.get("form_count", 0)
    if int(form_cnt) > 3:
        risk_score += 10

    hidden_elem = feature_vector.get("hidden_element_count", 0)
    if int(hidden_elem) > 5:
        risk_score += 8

    ext_link = feature_vector.get("external_link_ratio", 0.0)
    if float(ext_link) > 0.8:
        risk_score += 7

    # Riski maksimum 100'e sınırla
    risk_score = min(risk_score, 100)

    # Risk bazlı Label güncellemesi
    if risk_score >= 50:
        label = "PHISHING"
        risk_level = "Yüksek" if risk_score > 70 else "Orta"
    else:
        label = "LEGITIMATE"
        risk_level = "Orta" if risk_score > 30 else "Düşük"

    suspicious_features = _detect_suspicious(feature_vector)

    return {
        "label":               label,
        "confidence":          confidence,
        "risk_score":          risk_score,
        "risk_level":          risk_level,
        "suspicious_features": suspicious_features,
    }

if __name__ == "__main__":
    print("=" * 50)
    print("AI PHISHING - GERÇEK VERİ İLE MODEL EĞİTİMİ (SADECE URL)")
    print("=" * 50)
    train_and_save_model()

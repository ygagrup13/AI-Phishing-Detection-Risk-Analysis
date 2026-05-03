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

    Dataset Birleştirme:
    - dataset_phishing.csv  → url + status (phishing/legitimate)
    - phishing_site_urls.csv → URL + Label  (bad → 1, good → 0)
    - malicious_phish.csv   → url + type   (phishing → 1, benign → 0, others skip)
    - phishing.csv          → precomputed features + class (-1 → phishing=1, 1 → legitimate=0) [NO URL → skip]
"""

import os
import re
import sys
import warnings
import numpy as np
import pandas as pd
import joblib
from urllib.parse import urlparse
from difflib import SequenceMatcher

# Python modül yollarını çözmek için
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, f1_score

from features.url_features import URL_FEATURE_KEYS, extract_url_features

warnings.filterwarnings("ignore")

# Modelin kullanacağı sadece URL Feature'ları
FEATURE_COLUMNS = list(URL_FEATURE_KEYS)

DATA_DIR        = os.path.join(BASE_DIR, "data", "crawled_texts")
COMBINED_PATH   = os.path.join(BASE_DIR, "data", "combined_dataset.csv")
MODEL_PATH_V2   = os.path.join(BASE_DIR, "models", "model_v2.pkl")
MODEL_PATH      = os.path.join(BASE_DIR, "data", "rf_model.pkl")

_SUSPICIOUS_THRESHOLDS = {
    "has_https":                   ("==", 0),
    "has_at":                      ("==", 1),
    "dash_count":                  (">=", 3),
    "has_ip":                      ("==", 1),
    "subdomain_count":             (">=", 2),
    "suspicious_keyword_count":    (">=", 2),
    "is_suspicious_tld":           ("==", 1),
    "has_double_extension":        ("==", 1),
    "is_shortened":                ("==", 1),
    "https_in_domain":             ("==", 1),
    "has_redirect":                ("==", 1),
    "has_port":                    ("==", 1),
    "phishing_lexicon_mention_count": (">=", 3),
    "phishing_text_risk_0_100":    (">=", 40),
    "form_count":                  (">=", 2),
    "hidden_element_count":        (">=", 1),
    "favicon_foreign":             ("==", 1),
    "external_link_ratio":         (">=", 0.5),
    "urgency_score":               (">=", 3),
    "panic_score":                 (">=", 5),
    "typo_ratio":                  (">=", 0.3),
}

# ---------------------------------------------------------------------------
# Dataset yükleme ve birleştirme (DİNAMİK)
# ---------------------------------------------------------------------------

def _load_any_csv(path: str, max_rows: int = 100000) -> pd.DataFrame:
    """Verilen CSV'yi okur, URL ve Label (phishing/benign) kolonlarını otomatik bulup mapler."""
    try:
        # Önce kolonları okuyalım
        df = pd.read_csv(path, nrows=max_rows)
        
        # URL kolonunu bul
        url_col = next((col for col in df.columns if str(col).strip().lower() == "url"), None)
        if not url_col:
            print(f"[DATASET] ATLANDI: {os.path.basename(path)} (URL kolonu bulunamadı)")
            return pd.DataFrame(columns=["url", "label"])

        # Label/Status/Type kolonunu bul
        label_col = next((col for col in df.columns if str(col).strip().lower() in ["label", "status", "type", "class", "result"]), None)
        if not label_col:
            print(f"[DATASET] ATLANDI: {os.path.basename(path)} (Etiket kolonu bulunamadı)")
            return pd.DataFrame(columns=["url", "label"])

        # Veriyi çek
        df = df[[url_col, label_col]].rename(columns={url_col: "url", label_col: "raw_label"})
        df = df.dropna(subset=["url"])
        
        # Etiketleri normalize et
        def normalize_label(val):
            v = str(val).strip().lower()
            if v in ["phishing", "bad", "1", "1.0", "malware", "spam", "defacement"]:
                return 1
            elif v in ["legitimate", "benign", "good", "0", "0.0", "safe"]:
                return 0
            else:
                return -1 # Bilinmeyen
                
        df["label"] = df["raw_label"].apply(normalize_label)
        df = df[df["label"] >= 0][["url", "label"]]
        
        print(f"[DATASET] {os.path.basename(path)} yüklendi: {len(df)} geçerli satır")
        return df
    except Exception as e:
        print(f"[DATASET] HATA - {os.path.basename(path)} okunamadı: {e}")
        return pd.DataFrame(columns=["url", "label"])

def _build_combined_dataset() -> pd.DataFrame:
    dfs = []
    
    # DATA_DIR içindeki tüm CSV'leri bul (not-phishing.csv dahil)
    if os.path.exists(DATA_DIR):
        for file in os.listdir(DATA_DIR):
            if file.endswith(".csv"):
                file_path = os.path.join(DATA_DIR, file)
                dfs.append(_load_any_csv(file_path))
                
    if not dfs:
        raise FileNotFoundError(f"[HATA] {DATA_DIR} klasöründe hiçbir CSV dosyası bulunamadı!")

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined.drop_duplicates(subset=["url"])
    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"[DATASET] Toplam birleşik satır sayısı (duplicate temizlendi): {len(combined)}")
    return combined

# ---------------------------------------------------------------------------
# Eğitim fonksiyonu
# ---------------------------------------------------------------------------

def train_and_save_model():
    print("[ML MODEL] Datasetler birleştiriliyor...")
    df_combined = _build_combined_dataset()

    os.makedirs(os.path.dirname(COMBINED_PATH), exist_ok=True)
    df_combined.to_csv(COMBINED_PATH, index=False)
    print(f"[ML MODEL] Birleşik dataset kaydedildi: {COMBINED_PATH}")

    print(f"[ML MODEL] Ham URL'lerden Feature Extraction yapılıyor ({len(df_combined)} satır)...")

    def safe_extract(url_val):
        try:
            return extract_url_features(str(url_val))
        except Exception:
            return {k: 0 for k in FEATURE_COLUMNS}

    extracted_features = df_combined["url"].apply(safe_extract).tolist()
    df_features = pd.DataFrame(extracted_features)[FEATURE_COLUMNS]

    y = df_combined["label"].values

    print("[ML MODEL] Sadece URL feature'ları ile RandomForest eğitiliyor...")
    rf = RandomForestClassifier(
        n_estimators=100, random_state=42, max_depth=20, min_samples_leaf=1
    )

    scores_f1  = cross_val_score(rf, df_features, y, cv=3, scoring="f1")
    scores_acc = cross_val_score(rf, df_features, y, cv=3, scoring="accuracy")

    print(f"[ML MODEL] Accuracy (CV-3):  {scores_acc.mean():.4f} (±{scores_acc.std():.4f})")
    print(f"[ML MODEL] F1 Skoru (CV-3):  {scores_f1.mean():.4f} (±{scores_f1.std():.4f})")
    print(f"[ML MODEL] Kullanılan satır sayısı: {len(df_combined)}")

    rf.fit(df_features, y)

    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(rf, MODEL_PATH)
    print(f"[ML MODEL] Eğitim tamamlandı ve kaydedildi: {MODEL_PATH}\n")
    return rf

_global_model = None

def _get_model():
    global _global_model
    if _global_model is None:
        if os.path.exists(MODEL_PATH_V2):
            print("[ML MODEL] Yeni Pipeline modeli (v2) yükleniyor...")
            _global_model = joblib.load(MODEL_PATH_V2)
        elif os.path.exists(MODEL_PATH):
            print("[ML MODEL] Eski model (v1) yükleniyor...")
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

# ---------------------------------------------------------------------------
# 🔒 Localhost / Özel IP Kontrolü
# ---------------------------------------------------------------------------
def is_local_or_private(url: str) -> bool:
    """Localhost ve RFC-1918 özel IP aralıklarını tespit eder."""
    try:
        hostname = urlparse(url).hostname or ""
        private_patterns = [
            r'^127\.',
            r'^192\.168\.',
            r'^10\.',
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
            r'^localhost$',
            r'^0\.0\.0\.0$',
        ]
        return any(re.match(p, hostname) for p in private_patterns)
    except Exception:
        return False

def predict_phishing(feature_vector: dict) -> dict:
    # Localhost / özel ağ adresleri phishing değildir — analiz dışı
    url = feature_vector.get('_url', '')
    if url and is_local_or_private(url):
        print(f"[ML MODEL] Localhost/özel ağ tespit edildi, analiz atlanıyor: {url}")
        return {
            "label":               "LEGITIMATE",
            "confidence":          0.99,
            "risk_score":          5,
            "risk_level":          "Düşük",
            "suspicious_features": [],
            "note":                "Localhost/özel ağ adresi — analiz dışı",
        }

    # Bilinen markalar listesi
    KNOWN_BRANDS = [
        'google', 'microsoft', 'apple', 'amazon', 'facebook', 'instagram',
        'twitter', 'netflix', 'paypal', 'ebay', 'linkedin', 'youtube',
        'whatsapp', 'telegram', 'trendyol', 'hepsiburada', 'gittigidiyor',
        'sahibinden', 'ziraat', 'garanti', 'akbank', 'isbank', 'ykb',
        'turkiye', 'gov', 'edu', 'mil', 'dropbox', 'spotify', 'adobe',
        'steam', 'epicgames', 'binance', 'coinbase', 'tiktok'
    ]

    def is_typosquatting(url: str) -> tuple:
        try:
            hostname = urlparse(url).hostname or ""
            domain = hostname.replace('www.', '').split('.')[0].lower()
            for brand in KNOWN_BRANDS:
                if domain == brand:
                    return False, None
                ratio = SequenceMatcher(None, domain, brand).ratio()
                if 0.70 <= ratio < 1.0 and domain != brand:
                    return True, brand
        except:
            pass
        return False, None

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
    phishing_proba = proba

    # Base risk hesaplama
    if proba < 0.5:
        label = 'LEGITIMATE'
        base_risk = int(phishing_proba * 30)  # max 30 — meşru siteler için düşük tavan
    else:
        label = 'PHISHING'
        base_risk = int(50 + phishing_proba * 50)  # 50-100 arası — phishing için yüksek

    suspicious_features = _detect_suspicious(feature_vector)

    # Kural tabanlı NLP risk ekleme — sadece güçlü sinyaller
    additional_risk = 0

    # NLP sinyalleri — eşikler yükseltildi
    if float(feature_vector.get('phishing_tfidf_weighted_score', 0)) > 3.0:
        additional_risk += 15
        if 'phishing_tfidf_weighted_score' not in suspicious_features:
            suspicious_features.append('phishing_tfidf_weighted_score')

    if int(float(feature_vector.get('form_count', 0))) > 5:
        additional_risk += 10
        if 'form_count' not in suspicious_features:
            suspicious_features.append('form_count')

    if int(float(feature_vector.get('hidden_element_count', 0))) > 20:
        additional_risk += 8
        if 'hidden_element_count' not in suspicious_features:
            suspicious_features.append('hidden_element_count')

    if float(feature_vector.get('external_link_ratio', 0)) > 0.95:
        additional_risk += 7
        if 'external_link_ratio' not in suspicious_features:
            suspicious_features.append('external_link_ratio')

    if float(feature_vector.get('urgency_score', 0)) >= 8:
        additional_risk += 12
        if 'urgency_score' not in suspicious_features:
            suspicious_features.append('urgency_score')

    if float(feature_vector.get('panic_score', 0)) >= 8:
        additional_risk += 10
        if 'panic_score' not in suspicious_features:
            suspicious_features.append('panic_score')

    if float(feature_vector.get('typo_ratio', 0)) > 0.6:
        additional_risk += 8
        if 'typo_ratio' not in suspicious_features:
            suspicious_features.append('typo_ratio')

    if int(float(feature_vector.get('input_count', 0))) > 10:
        additional_risk += 5
        if 'input_count' not in suspicious_features:
            suspicious_features.append('input_count')

    risk_score = min(base_risk + additional_risk, 100)

    # Risk bazlı Label güncellemesi
    if risk_score >= 50:
        label = "PHISHING"
    else:
        label = "LEGITIMATE"

    if risk_score <= 40:
        risk_level = "Düşük"
    elif risk_score <= 70:
        risk_level = "Orta"
    else:
        risk_level = "Yüksek"


    # Typosquatting kontrolü
    is_typo, similar_brand = is_typosquatting(feature_vector.get('_url', ''))
    if is_typo and similar_brand:
        suspicious_features.append('typosquatting')
        risk_score = min(risk_score + 40, 100)
        return {
            "label": "PHISHING",
            "confidence": 0.95,
            "risk_score": risk_score,
            "risk_level": "Yüksek",
            "suspicious_features": suspicious_features,
            "warning": f"'{similar_brand}' markasını taklit eden şüpheli domain tespit edildi"
        }

    # Şüpheli özellik yoksa kesinlikle LEGITIMATE
    if len(suspicious_features) == 0:
        legitimate_proba = round(1.0 - confidence, 4)
        return {
            "label": "LEGITIMATE",
            "confidence": legitimate_proba,
            "risk_score": max(risk_score, 5),
            "risk_level": "Düşük",
            "suspicious_features": [],
        }

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

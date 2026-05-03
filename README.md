# 🛡️ PhishGuard AI — Yapay Zeka Destekli Phishing Tespit Sistemi

> Fırat Üniversitesi Yazılım Mühendisliği Bölümü 

---

## 📌 Proje Hakkında

PhishGuard AI, kullanıcıların şüpheli web sitelerini saniyeler içinde analiz edebilmesini sağlayan, yapay zeka tabanlı bir phishing tespit ve risk analizi sistemidir.

Mevcut antivirüs yazılımları yalnızca bilinen phishing listelerine bakarken, PhishGuard AI hem URL yapısını hem de sayfa içeriğini (NLP) analiz ederek **henüz tanınmamış saldırıları bile tespit edebilmektedir.**

---

## 👥 Ekip

| İsim | Rol | Modül |
|------|-----|-------|
| Zelal Ergin | Scrum Master + URL Feature Extraction | `features/url_features.py` |
| Mehmet Polat Maç | Web Crawler | `crawler/web_crawler.py` |
| Muhammed Kayra Doğan | Text Analysis (NLP) | `features/text_features.py` |
| Meryem Tekeli | Machine Learning Model | `model/ml_model.py` |

---

## 🚀 Özellikler

### 🔗 URL Analizi (20 Feature)
- URL uzunluğu, HTTPS kullanımı, @ karakteri, tire sayısı
- IP adresi kullanımı, subdomain sayısı, özel karakter sayısı
- Shannon Entropy hesabı, kısaltılmış link tespiti
- Şüpheli TLD tespiti (`.xyz`, `.tk`, `.ml` vb.)
- Çift uzantı tespiti, domain içi HTTPS kelimesi
- 27 şüpheli anahtar kelime kontrolü

### 🧠 NLP & HTML Analizi (11 Feature)
- TF-IDF tabanlı phishing kelime ağırlıklandırması
- Türkçe + İngilizce phishing kelime sözlüğü (30+ kelime)
- Aciliyet/manipülasyon ifadesi tespiti
- Panik/korku tonu analizi
- Yazım hatası oranı hesabı
- Form, input, gizli element sayısı
- Dış link oranı, favicon domain kontrolü

### 🎭 Typosquatting Tespiti
- 35+ bilinen marka ile benzerlik karşılaştırması
- `nicrosoft.com`, `paypa1.com` gibi sahte domainleri tespit eder
- SequenceMatcher ile %70+ benzerlik eşiği

### 🤖 Makine Öğrenmesi Modeli
- **107.000+ gerçek veri** ile eğitilmiş Random Forest
- **%88.38 Accuracy**, **%88.77 F1 Score**
- Logistic Regression ve SVM ile karşılaştırma yapılmış
- 5-katlı çapraz doğrulama (Cross-Validation)

### 🌐 Cloudflare Browser Rendering API
- JavaScript render eden siteler için gelişmiş tarama
- BeautifulSoup crawler'ına otomatik fallback
- `USE_CLOUDFLARE = True` ile aktif edilir

---

## 📊 Sistem Mimarisi

```
Kullanıcı URL girer
        ↓
Web Crawler (BeautifulSoup / Cloudflare API)
        ↓
Feature Extraction
    ├── URL Features (20 özellik)
    └── NLP & HTML Features (11 özellik)
        ↓
ML Model (Random Forest)
        ↓
Risk Skoru (0-100) + Şüpheli Özellikler
        ↓
Web Arayüzü (FastAPI + HTML/CSS/JS)
```

---

## 🛠️ Kurulum

### Gereksinimler
- Python 3.10+
- pip

### Adımlar

```bash
# Repoyu klonla
git clone https://github.com/ygagrup13/AI-Phishing-Detection-Risk-Analysis.git
cd AI-Phishing-Detection-Risk-Analysis/phishing_ai_project

# Kütüphaneleri yükle
pip install -r requirements.txt

# API'yi başlat
py api.py
```

Tarayıcıda `http://127.0.0.1:8000` adresini aç.

---

## 📁 Proje Yapısı

```
phishing_ai_project/
├── crawler/
│   └── web_crawler.py          # Web crawler (BeautifulSoup + Cloudflare)
├── features/
│   ├── url_features.py         # 20 URL feature extraction
│   └── text_features.py        # 11 NLP & HTML feature extraction
├── model/
│   └── ml_model.py             # Random Forest model + tahmin
├── frontend/
│   └── index.html              # Web arayüzü
├── data/
│   ├── rf_model.pkl            # Eğitilmiş model
│   └── combined_dataset.csv    # Birleştirilmiş dataset
├── api.py                      # FastAPI REST endpoint
├── main.py                     # Terminal arayüzü
├── start.bat                   # Tek tıkla başlatma (Windows)
└── requirements.txt
```

---

## 🎯 Kullanım

### Web Arayüzü
```bash
py api.py
# Tarayıcıda http://127.0.0.1:8000 aç
```

### Terminal
```bash
py main.py
```

### API (REST)
```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://secure-login-paypal.xyz/update-account"}'
```

**Örnek API Çıktısı:**
```json
{
  "url": "http://secure-login-paypal.xyz/update-account",
  "label": "PHISHING",
  "confidence": 0.95,
  "risk_score": 90,
  "risk_level": "Yüksek",
  "suspicious_features": [
    "has_https",
    "dash_count",
    "suspicious_keyword_count",
    "is_suspicious_tld"
  ]
}
```

---

## 📈 Model Performansı

| Metrik | Skor |
|--------|------|
| Accuracy | %88.38 |
| F1 Score | %88.77 |
| Precision | %91.23 |
| Recall | %84.40 |
| False Positive Rate | %8.11 |

**Eğitim Verisi:** 107.000+ URL (phishing + legitimate)

**Kullanılan Datasettler:**
- Web Page Phishing Detection Dataset (Kaggle)
- Phishing Site URLs (Kaggle)
- Malicious URLs Dataset (Kaggle)

---

## 🧪 Test Sonuçları

| URL | Beklenen | Sonuç | Risk |
|-----|----------|-------|------|
| `https://www.google.com` | GÜVENLİ | ✅ GÜVENLİ | 8 |
| `https://www.trendyol.com` | GÜVENLİ | ✅ GÜVENLİ | 19 |
| `http://secure-login-paypal.xyz` | PHİSHİNG | ✅ PHİSHİNG | 95 |
| `https://nicrosoft.com` | PHİSHİNG | ✅ PHİSHİNG | 80 |
| `https://paypa1.com` | PHİSHİNG | ✅ PHİSHİNG | 65 |

---

## 🔧 Teknolojiler

| Kategori | Teknoloji |
|----------|-----------|
| Backend | Python, FastAPI |
| ML | scikit-learn, Random Forest |
| NLP | TF-IDF, BeautifulSoup |
| URL Analizi | tldextract, urllib |
| Web Crawler | requests, BeautifulSoup, Cloudflare API |
| Frontend | HTML, CSS, JavaScript |
| Veri | pandas, numpy |

---

## 📄 Lisans

Bu proje, Fırat Üniversitesi Yazılım Mühendisliği Bölümü Yazılım Gereksinim Analizi dersi kapsamında, grup çalışması olarak akademik amaçlarla geliştirilmiştir.

---

## *PhishGuard AI — "Bir linke tıklamadan önce düşünmek yerine, sistem düşünsün."*

<div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/scikit--learn-RandomForest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
<img src="https://img.shields.io/badge/Cloudflare-Browser%20Rendering-F38020?style=for-the-badge&logo=cloudflare&logoColor=white"/>
<img src="https://img.shields.io/badge/Accuracy-88.14%25-brightgreen?style=for-the-badge"/>

# 🛡️ PhishGuard AI
### Yapay Zeka Destekli Phishing Tespit & Risk Analizi Sistemi

> **Fırat Üniversitesi · Yazılım Mühendisliği Bölümü**  
> Yazılım Gereksinim Analizi Dersi — Grup Projesi

*"Bir linke tıklamadan önce düşünmek yerine, sistem düşünsün."*

</div>

---

## 📌 Proje Hakkında

**PhishGuard AI**, kullanıcıların şüpheli web sitelerini saniyeler içinde analiz edebilmesini sağlayan, çok katmanlı yapay zeka tabanlı bir **phishing tespit ve risk analizi** sistemidir.

Geleneksel antivirüs yazılımları yalnızca bilinen phishing listelerine (kara listeler) bakarken, PhishGuard AI hem **URL yapısını** hem de **sayfa içeriğini (NLP)** gerçek zamanlı olarak analiz ederek **henüz kara listeye alınmamış, sıfır-gün saldırılarını bile tespit edebilmektedir.**

### 🎯 Neden PhishGuard AI?

| Özellik | Geleneksel Çözümler | PhishGuard AI |
|--------|---------------------|---------------|
| Bilinmeyen saldırı tespiti | ❌ | ✅ |
| URL yapısal analizi | ❌ | ✅ (21 özellik) |
| NLP içerik analizi | ❌ | ✅ (11 özellik) |
| Typosquatting tespiti | ❌ | ✅ (35+ marka) |
| IDN/Punycode homoğlif tespiti | ❌ | ✅ |
| JavaScript render desteği | ❌ | ✅ (Cloudflare API) |
| Gerçek zamanlı REST API | ❌ | ✅ |
| Türkçe phishing tespiti | ❌ | ✅ |

---

## 👥 Geliştirici Ekip

| İsim | Rol | Sorumlu Modüller |
|------|-----|------------------|
| **Zelal Ergin** | Scrum Master + URL Feature Extraction | `features/url_features.py` |
| **Mehmet Polat Maç** | Web Crawler Geliştirici | `crawler/web_crawler.py` |
| **Muhammed Kayra Doğan** | NLP & Text Analizi | `features/text_features.py` |
| **Meryem Tekeli** | ML Model Eğitimi + Risk Skoru + Güven Oranı + Web Arayüzü | `model/ml_model.py`, `model/train_v2.py`, `frontend/index.html` |

---

## 🚀 Özellikler

### 🔗 URL Analizi — 21 Özellik

URL yapısından çıkarılan sayısal özellikler Random Forest modeline beslenir:

| Özellik | Açıklama |
|---------|----------|
| `url_length` | URL toplam uzunluğu |
| `has_https` | HTTPS protokolü kullanımı |
| `has_at` | `@` karakteri içeriyor mu |
| `dash_count` | Tire (`-`) sayısı |
| `has_ip` | Domain yerine IP adresi kullanımı |
| `subdomain_count` | Alt domain sayısı |
| `special_char_count` | `?`, `=`, `&`, `%`, `#` sayısı |
| `has_port` | Non-standart port kullanımı |
| `digit_count` | Rakam sayısı |
| `has_redirect` | Path içinde `//` yönlendirme |
| `suspicious_keyword_count` | 27 şüpheli kelime sayısı |
| `domain_length` | Domain adı uzunluğu |
| `is_suspicious_tld` | `.xyz`, `.tk`, `.ml`, `.ga`, `.cf` tespiti |
| `path_length` | URL path uzunluğu |
| `url_entropy` | Shannon Entropy (rastgelelik ölçüsü) |
| `is_shortened` | Kısaltma servisi tespiti (bit.ly, tinyurl…) |
| `dot_count` | Nokta sayısı |
| `digit_ratio` | URL'deki rakam oranı |
| `has_double_extension` | Çift uzantı tespiti (`.com.verify`) |
| `https_in_domain` | Domain içinde `https` kelimesi |
| `is_trusted_tld` | `.edu.tr`, `.gov.tr`, `.mil` güvenilir uzantı |

### 🧠 NLP & HTML Analizi — 11 Özellik

Sayfa içeriğinden kural tabanlı olarak risk skoruna yansıtılan özellikler:

| Özellik | Açıklama |
|---------|----------|
| `phishing_tfidf_weighted_score` | TF-IDF ağırlıklı phishing kelime skoru |
| `phishing_lexicon_mention_count` | 30+ phishing kelimesinin geçiş sayısı |
| `phishing_text_risk_0_100` | 0-100 normalize edilmiş metin risk skoru |
| `form_count` | `<form>` etiketi sayısı |
| `input_count` | `<input>` etiketi sayısı |
| `external_link_ratio` | Farklı domaine giden link oranı |
| `hidden_element_count` | `display:none` / `visibility:hidden` element sayısı |
| `favicon_foreign` | Favicon farklı domaindan mı geliyor? |
| `urgency_score` | Aciliyet/manipülasyon ifadesi sayısı |
| `typo_ratio` | Yazım hatası oranı |
| `panic_score` | Panik/korku tonu skoru |

### 🎭 Gelişmiş Typosquatting & Homoğlif Tespiti

35+ bilinen marka ile çok katmanlı benzerlik analizi:

- **Leet-speak normalizasyonu**: `g00gle` → `google`, `paypa1` → `paypal`
- **Unicode homoğlif haritalaması**: Kiril, Latin varyantları (`ı`, `а`, `е`, `о`, `р`, `с`, `х`, `у`)
- **IDN/Punycode çözme**: `xn--ncrosoft-tkb` → `mıcrosoft` → `microsoft`
- **SequenceMatcher**: %70+ benzerlik eşiği ile bulanık eşleşme
- **Tire saldırısı**: `secure-login-paypal.xyz` → `paypal` markası tespit edilir
- **Resmi kısa domain koruması**: `youtu.be`, `t.co`, `fb.com` gibi resmi kısa domainler yanlış alarm vermez

### 🌐 Çift Katmanlı Web Crawler

```
İstek Geldi
     │
     ▼
USE_CLOUDFLARE = True?
     │
     ├─ EVET → Cloudflare Browser Rendering API
     │              (JavaScript render eder)
     │              Başarısız olursa ↓
     └─ HAYIR / FALLBACK → BeautifulSoup Crawler
                               (Hızlı, SSL-bypass destekli)
```

**Cloudflare Browser Rendering API**: JavaScript ile dinamik yüklenen sayfaları (SPA, React, Vue) tam olarak render ederek analiz eder. BeautifulSoup bu tür sayfaları eksik okur.

| Özellik | BeautifulSoup | Cloudflare API |
|---------|--------------|----------------|
| JavaScript desteği | ❌ | ✅ |
| SPA/React/Vue sayfaları | ❌ | ✅ |
| Hız | ✅ Hızlı | 🟡 Orta |
| API anahtarı gerekli | ❌ | ✅ |
| Fallback | — | ✅ BS4'e düşer |

---

## ☁️ Cloudflare Browser Rendering API Entegrasyonu

Proje, JavaScript render eden modern web sitelerini analiz edebilmek için **Cloudflare Browser Rendering API** ile entegre edilmiştir.

### Neden Gerekli?

Günümüz phishing siteleri çoğunlukla React, Vue veya Angular ile geliştirilmektedir. Geleneksel `requests + BeautifulSoup` yaklaşımı bu sayfalarda yalnızca boş bir `<div id="root">` görür; gerçek içerik JavaScript çalıştıktan sonra yüklenir. Cloudflare API bu sorunu çözer.

### Nasıl Çalışır?

```
Kullanıcı URL girer
        │
        ▼
[api.py] USE_CLOUDFLARE = True
        │
        ▼
POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/browser-rendering/content
Body: { "url": "https://hedef-site.com" }
        │
        ▼
Cloudflare gerçek bir Chrome tarayıcısı açar
JavaScript çalıştırır, sayfayı tam render eder
        │
        ▼
Response: { "result": { "text": "...", "html": "..." } }
        │
        ├─ Başarılı → HTML + text döner (NLP analizi yapılır)
        └─ Hata (timeout, 4xx) → crawl_site() fallback (BeautifulSoup)
```

### Entegrasyon Detayları

```python
# crawler/web_crawler.py
CLOUDFLARE_ACCOUNT_ID = "..."      # Cloudflare hesap ID
CLOUDFLARE_API_TOKEN  = "cfut_..." # Bearer token

requests.post(
    f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/browser-rendering/content",
    headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"},
    json={"url": url},
    timeout=20
)
```

### Aktif/Pasif Etme

```python
# api.py — satır 25
USE_CLOUDFLARE = True   # Cloudflare Browser Rendering API aktif
USE_CLOUDFLARE = False  # Sadece BeautifulSoup kullan (hız önceliği)
```

> **Not**: Cloudflare API anahtarı `web_crawler.py` içinde sabit olarak tanımlıdır. Üretim ortamında `.env` dosyasına taşımanız önerilir.

---


## 📊 Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────┐
│                     KULLANICI                           │
│              URL girer → Web Arayüzü                    │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP POST /analyze
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI (api.py)                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │  1. URL Format Doğrulama (validate_url)         │    │
│  │  2. Bilinen Güvenli Domain Kontrolü             │    │
│  │     (SAFE_DOMAINS listesi + YouTube oEmbed)     │    │
│  └──────────────────┬──────────────────────────────┘    │
└─────────────────────┼───────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ Crawler  │ │  URL     │ │  Text    │
   │(CF/BS4)  │ │Features  │ │Features  │
   │          │ │(21 feat) │ │(11 feat) │
   └────┬─────┘ └────┬─────┘ └────┬─────┘
        └────────────┼─────────────┘
                     │ Feature Vector (32 özellik)
                     ▼
         ┌───────────────────────┐
         │   ML Model (ml_model) │
         │  ┌──────────────────┐ │
         │  │ Random Forest    │ │
         │  │ (107K+ veriyle   │ │
         │  │  eğitilmiş)      │ │
         │  └────────┬─────────┘ │
         │           │           │
         │  ┌────────▼─────────┐ │
         │  │ Kural Tabanlı    │ │
         │  │ Risk Düzeltici   │ │
         │  │ + Typosquatting  │ │
         │  │   Kontrolü       │ │
         │  └────────┬─────────┘ │
         └───────────┼───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Sonuç Döndürülür:     │
        │  • label (PHISHING /   │
        │    LEGITIMATE /        │
        │    ERİŞİLEMEYEN)      │
        │  • risk_score (0-100)  │
        │  • confidence          │
        │  • suspicious_features │
        └────────────────────────┘
```

---

## 📈 Model Performansı

### Karşılaştırmalı Model Analizi

| Model | Validation F1 | CV F1 (5-fold) |
|-------|--------------|----------------|
| Logistic Regression | 0.7632 | 0.7677 |
| HistGradientBoosting (XGBoost-like) | 0.8737 | 0.8703 |
| **Random Forest** ✅ | **0.8762** | **0.8707** |

### Seçilen Model: Random Forest — Test Seti Sonuçları

| Metrik | Değer |
|--------|-------|
| **Accuracy** | **%88.14** |
| **F1 Score** | **%87.68** |
| **Precision** | **%91.23** |
| **Recall** | **%84.40** |
| **False Positive Rate** | **%8.11** |

### Confusion Matrix

```
              Tahmin: SAFE   Tahmin: PHİSHİNG
Gerçek: SAFE      4135            365       ← False Positive (FP)
Gerçek: PHİSH      702           3798       ← True Positive  (TP)
```

> **Eğitim Verisi**: 107.000+ URL (phishing + legitimate karışık)  
> **Doğrulama**: 3-katlı ve 5-katlı çapraz doğrulama (Cross-Validation)

### Kullanılan Veri Setleri

| Dosya | Kaynak | Boyut | İçerik |
|-------|--------|-------|--------|
| `dataset_phishing.csv` | Kaggle — Web Page Phishing Detection | ~3.5 MB | URL + durum (phishing/legitimate) |
| `phishing_site_urls.csv` | Kaggle — Phishing Site URLs | ~30 MB | URL + etiket (bad/good), 549.346 satır |
| `malicious_phish.csv` | Kaggle — Malicious URLs Dataset | ~43 MB | URL + tür (phishing/benign/malware/defacement) |
| `not-phishing.csv` | Özel derleme — Meşru URL listesi | ~102 MB | Yalnızca legitimate URL'ler |
| `phishing.csv` | UCI ML Repository | ~855 KB | Önceden hesaplanmış özellikler + sınıf etiketi |
| `phishing-urls.csv` | Özel derleme — Phishing URL listesi | ~81 KB | Phishing URL'leri |
| `legitimate-urls.csv` | Özel derleme — Güvenli URL listesi | ~64 KB | Meşru URL'ler |
| `uci-ml-phishing-dataset.csv` | UCI Machine Learning Repository | ~824 KB | Klasik UCI phishing feature seti |

> 📦 **Toplam ham veri**: ~180 MB+ · **Eğitime katılan (duplicate temizlendi)**: ~250.000+ benzersiz URL

---

## 🧪 Test Sonuçları

| URL | Beklenen | Sonuç | Risk Skoru |
|-----|----------|-------|------------|
| `https://www.google.com` | GÜVENLİ | ✅ LEGITIMATE | 5 |
| `https://www.trendyol.com` | GÜVENLİ | ✅ LEGITIMATE | 19 |
| `https://github.com` | GÜVENLİ | ✅ LEGITIMATE | 5 |
| `https://youtu.be/Pt-TPo05fdI` | GÜVENLİ | ✅ LEGITIMATE | 5 |
| `http://secure-login-paypal.xyz/update-account` | PHİSHİNG | ✅ PHISHING | 95 |
| `https://nicrosoft.com` | PHİSHİNG | ✅ PHISHING | 80 |
| `https://paypa1.com` | PHİSHİNG | ✅ PHISHING | 65 |
| `http://xn--mcrosoft-tkb.com` (mıcrosoft) | PHİSHİNG | ✅ PHISHING | 90 |
| `http://g00gle-verify.tk/signin` | PHİSHİNG | ✅ PHISHING | 98 |

---

## 🔒 Güvenlik Katmanları

```
Katman 1: URL Format Doğrulama
  └── Protokol, domain yapısı, TLD minimum uzunluğu

Katman 2: Bilinen Güvenli Domain Bypass
  └── SAFE_DOMAINS listesi + YouTube oEmbed doğrulama
  └── Eğitim/Devlet kurumu otomatik tanıma (.edu.tr, .gov.tr)

Katman 3: URL Yapısal Analizi (21 Feature)
  └── Entropi, şüpheli kelimeler, TLD, IP kullanımı...

Katman 4: NLP & HTML İçerik Analizi (11 Feature)
  └── TF-IDF, form sayısı, gizli elementler, aciliyet skoru...

Katman 5: Typosquatting & Homoğlif Motoru
  └── Leet-speak + Unicode + IDN/Punycode + SequenceMatcher

Katman 6: Random Forest ML Tahmini
  └── 107K+ örnekle eğitilmiş, %88 accuracy

Katman 7: Kural Tabanlı Risk Düzeltici
  └── NLP sinyalleri + protokol typosquatting + trusted TLD
```

---

## 🛠️ Kurulum

### Gereksinimler

- Python 3.10+
- pip

### Hızlı Başlangıç

```bash
# 1. Repoyu klonla
git clone https://github.com/ygagrup13/AI-Phishing-Detection-Risk-Analysis.git

# 2. Proje dizinine gir
cd AI-Phishing-Detection-Risk-Analysis/phishing_ai_project

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. API'yi başlat
python api.py
```

Tarayıcıda `http://127.0.0.1:8000` adresini açın.

### Windows — Tek Tıkla Başlatma

```bash
start.bat
```

---

## 📁 Proje Yapısı

```
AI-Phishing-Detection-Risk-Analysis/
│
├── phishing_ai_project/
│   ├── crawler/
│   │   └── web_crawler.py          # BeautifulSoup + Cloudflare API crawler
│   │
│   ├── features/
│   │   ├── url_features.py         # 21 URL özelliği çıkarımı + Entropy
│   │   └── text_features.py        # 11 NLP & HTML özelliği (TF-IDF, urgency, panic)
│   │
│   ├── model/
│   │   ├── ml_model.py             # Random Forest + Typosquatting + Risk motoru
│   │   └── train_v2.py             # Model yeniden eğitim pipeline'ı
│   │
│   ├── frontend/
│   │   └── index.html              # Web arayüzü (Gauge, animasyonlar, risk kartları)
│   │
│   ├── data/
│   │   ├── rf_model.pkl            # Eğitilmiş Random Forest modeli
│   │   └── combined_dataset.csv    # Birleştirilmiş ve temizlenmiş dataset
│   │
│   ├── models/
│   │   └── model_v2.pkl            # Pipeline tabanlı v2 model (varsa öncelikli yüklenir)
│   │
│   ├── api.py                      # FastAPI REST API (ana giriş noktası)
│   ├── main.py                     # Terminal arayüzü
│   ├── requirements.txt            # Python bağımlılıkları
│   ├── start.bat                   # Windows için tek tıkla başlatma
│   └── evaluation_report.md        # Model karşılaştırma raporu
│
├── test_url_features.py            # URL feature unit testleri
├── test_advanced_crawler.py        # Cloudflare crawler testleri
├── test_supabase.py                # Veritabanı bağlantı testi
└── README.md
```

---

## 🎯 Kullanım

### 1. Web Arayüzü (Önerilen)

```bash
python api.py
# Tarayıcıda http://127.0.0.1:8000 aç
```

URL girin → Analiz Et butonuna basın → Sonuçları görün:
- 🟢 **GÜVENLİ** — Risk skoru düşük, şüpheli özellik yok
- 🔴 **PHİSHİNG** — Yüksek risk, şüpheli özellikler listelenir
- 🟡 **ERİŞİLEMEYEN** — Site açılmıyor, typosquatting yoksa belirsiz

### 2. Terminal Arayüzü

```bash
python main.py
```

### 3. REST API

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://secure-login-paypal.xyz/update-account"}'
```

**Örnek API Yanıtı:**

```json
{
  "url": "http://secure-login-paypal.xyz/update-account",
  "status": "success",
  "label": "PHISHING",
  "confidence": 0.95,
  "risk_score": 95,
  "risk_level": "Yüksek",
  "suspicious_features": [
    "has_https",
    "dash_count",
    "suspicious_keyword_count",
    "is_suspicious_tld",
    "typosquatting"
  ],
  "warning": "'paypal' markasını taklit eden şüpheli domain tespit edildi"
}
```

### 4. API Dokümantasyonu (Swagger UI)

```
http://127.0.0.1:8000/docs
```

---

## 🔧 Teknoloji Yığını

| Katman | Teknoloji | Kullanım Amacı |
|--------|-----------|----------------|
| **Backend API** | FastAPI + Uvicorn | REST API sunucusu |
| **ML Engine** | scikit-learn RandomForest | Phishing sınıflandırması |
| **NLP** | TF-IDF (scikit-learn) | Metin ağırlıklandırması |
| **Web Crawler** | requests + BeautifulSoup4 | Sayfa içeriği çekme |
| **JS Render** | Cloudflare Browser Rendering API | SPA/dinamik sayfa desteği |
| **URL Analizi** | tldextract + urllib | TLD ve domain ayrıştırma |
| **Veri** | pandas + numpy | Dataset işleme |
| **Model Kaydetme** | joblib | Model serileştirme |
| **Frontend** | HTML5 + CSS3 + Vanilla JS | Web arayüzü |
| **Veri Doğrulama** | Pydantic | API şema doğrulama |

---

## ⚙️ Konfigürasyon

### Cloudflare API Anahtarı

```python
# crawler/web_crawler.py içinde
CLOUDFLARE_ACCOUNT_ID = "<hesap-id>"
CLOUDFLARE_API_TOKEN  = "cfut_<token>"
```

```python
# api.py içinde (satır 25)
USE_CLOUDFLARE = True   # Cloudflare Browser Rendering API aktif
USE_CLOUDFLARE = False  # Sadece BeautifulSoup kullan
```

### Model Versiyonu

Sistem önce `models/model_v2.pkl` (pipeline), bulamazsa `data/rf_model.pkl` (legacy) yükler. İkisi de yoksa otomatik eğitim başlatır.

### Modeli Yeniden Eğitmek

```bash
cd phishing_ai_project
python model/ml_model.py
# veya
python model/train_v2.py
```

---

## 🧩 Modüller Detaylı

### `crawler/web_crawler.py`

- `crawl_site(url)` — BeautifulSoup ile sayfa çeker, metni temizler, linkleri bulur
- `crawl_with_cloudflare(url)` — Cloudflare API ile JS render; başarısız olursa `crawl_site`'a düşer
- `crawl_recursive(url, max_pages, max_depth)` — Alt sayfaları BFS ile tarar
- `clean_text(text)` — HTML gürültüsünü temizler, anlamsız satırları filtreler

### `features/url_features.py`

- `extract_url_features(url)` — 21 sayısal özellik döndürür
- `calculate_entropy(text)` — Shannon Entropy hesaplar
- `is_trusted_tld(url)` — `.edu.tr`, `.gov.tr` gibi güvenilir uzantıları tanır
- `URL_FEATURE_KEYS` — Modelin beklediği sıralı feature listesi

### `features/text_features.py`

- `extract_text_features(page_text, html)` — 11 NLP & HTML özelliği döndürür
- TF-IDF vektörleyici modül yüklenirken hazır corpus ile eğitilir (one-time)
- İngilizce + Türkçe 30+ phishing kelime sözlüğü
- E-ticaret whitelist: kampanya kelimeleri yanlış alarm vermez

### `model/ml_model.py` + `model/train_v2.py` *(Meryem Tekeli)*

Modelin tüm eğitim süreci, risk hesaplama mantığı ve güven oranı Meryem tarafından tasarlanmıştır:

| Bileşen | Açıklama |
|---------|----------|
| **Model Eğitimi** | 8 farklı CSV veri setini birleştirme, duplicate temizleme, ~250.000+ URL ile Random Forest eğitimi |
| **3-Fold Cross Validation** | Eğitim sırasında hem F1 hem Accuracy CV skorları hesaplanır |
| **Risk Skoru (0-100)** | `LEGITIMATE` → `phishing_proba × 30` (max 30), `PHISHING` → `50 + phishing_proba × 50` (50-100) |
| **Güven Oranı** | Model `predict_proba()` çıktısı; frontend'de `LEGITIMATE` için `100 - risk_score`, `PHISHING` için `risk_score` olarak gösterilir |
| **Kural Tabanlı Risk Düzeltici** | NLP sinyalleri (TF-IDF, form, hidden, urgency, panic) ek puan ekler; trusted TLD ise -40 puan indirim |
| **Risk Seviyesi Etiketleme** | `≤40` → Düşük, `41-70` → Orta, `>70` → Yüksek |
| **Typosquatting Motoru** | 7 katman: leet-speak, Unicode homoğlif, IDN/Punycode çözme, tire saldırısı, SequenceMatcher |
| **Model Versiyonlama** | `model_v2.pkl` (pipeline) → `rf_model.pkl` (legacy) → Yoksa otomatik eğitim |
| `predict_phishing(feature_vector)` | Ana tahmin fonksiyonu — tüm katmanları sırayla çalıştırır |
| `train_and_save_model()` | Sıfırdan model eğitir, cross-validation yapar, joblib ile kaydeder |
| `_detect_suspicious(feature_vector)` | 21 özellik için eşik tabanlı şüpheli özellik tespiti |
| `is_local_or_private(url)` | Localhost/RFC-1918 özel ağ bypass |

### `api.py`

- `POST /analyze` — Ana analiz endpoint'i
- `GET /` — Web arayüzünü serve eder
- `is_known_safe_domain(url)` — Güvenli domain bypass + YouTube oEmbed doğrulama
- `validate_url(url)` — Sadece yapısal URL doğrulama (ağ isteği olmadan)

### `frontend/index.html` *(Meryem Tekeli)*

Tek sayfalık web arayüzü — tüm UI/UX Meryem tarafından tasarlanmış ve geliştirilmiştir:

| Bileşen | Açıklama |
|---------|----------|
| **Animated Particle Network** | Canvas üzerinde 80 parçacık + aralarında bağlantı çizgileri; mor-mavi renk geçişi |
| **Glassmorphism Tasarım** | `backdrop-filter: blur(20px)` + mor kenarlıklı şeffaf kartlar |
| **Orbitron + Inter Fontları** | Google Fonts — siber güvenlik temalı tipografi |
| **Risk Gauge (SVG Dairesel İlerleme)** | Risk skoru (0-100) animasyonlu dairesel gösterge; renk: 🟢 Düşük / 🟡 Orta / 🔴 Yüksek |
| **Güven Oranı Hesaplama** | `LEGITIMATE` → `%{100 - risk_score} güvenli`, `PHISHING` → `%{risk_score} risk` olarak gösterilir |
| **Analiz Animasyonu** | 6 adımlı sıralı step animasyonu (crawler → NLP → ML → sonuç) |
| **Şüpheli Özellikler Kartı** | Her özellik için Türkçe açıklamalı renkli badge'ler (22 özellik etiketlenmiş) |
| **URL Bilgileri Tablosu** | Domain, protokol, path, URL uzunluğu satır bazlı gösterim |
| **Feature Analizi Kartı** | Ham feature değerleri görsel olarak listelenir |
| **ERİŞİLEMEYEN Özel Ekranı** | Sarı uyarı ekranı — gauge sıfırlanır, ikincil kartlar gizlenir, büyük uyarı mesajı gösterilir |
| **Hata Kartı** | API bağlantısı kurulamazsa kullanıcıya terminal komutu gösterilir |
| **Responsive Grid** | 900px üstünde 3 sütunlu kart düzeni, mobilde tek sütun |

---

## 🔍 Phishing Tespiti Mantığı (Akış)

```
1. URL Format Kontrolü
   ├─ Geçersiz → "GEÇERSİZ URL" döndür
   └─ Geçerli → devam

2. Bilinen Güvenli Domain Kontrolü
   ├─ Güvenli domain → risk_score=5, label=LEGITIMATE döndür
   └─ Bilinmiyor → devam

3. Web Crawler (Cloudflare → BeautifulSoup fallback)
   └─ page_text, html topla

4. Feature Extraction
   ├─ URL Features (21 özellik)
   └─ Text/HTML Features (11 özellik)

5. Typosquatting Kontrolü (ML'den ÖNCE)
   ├─ Typosquatting bulundu → PHISHING (site kapalı olsa bile)
   └─ Temiz → devam

6. Site Erişilebilirlik Kontrolü
   ├─ page_text < 50 karakter → ERİŞİLEMEYEN döndür
   └─ Erişilebilir → devam

7. Random Forest ML Tahmini
   └─ P(phishing) → base_risk hesapla

8. Kural Tabanlı Risk Düzeltici
   ├─ NLP sinyalleri ekle (TF-IDF, form, hidden, urgency, panic...)
   ├─ Protokol typosquatting kontrolü (hllps://, httos://...)
   └─ Trusted TLD ise risk düşür (-40 puan)

9. Final Karar
   ├─ risk_score >= 50 → PHISHING
   └─ risk_score < 50  → LEGITIMATE
```

---

## 📄 Lisans

Bu proje, **Fırat Üniversitesi Yazılım Mühendisliği Bölümü** Yazılım Gereksinim Analizi dersi kapsamında, akademik amaçlarla geliştirilmiştir.

Ticari kullanım için lütfen geliştirici ekiple iletişime geçin.

---

<div align="center">

**🛡️ PhishGuard AI** — Fırat Üniversitesi · 2025–2026

*~250.000+ URL · %88.14 Accuracy · 7 Katmanlı Güvenlik · Türkçe + İngilizce Destek*

</div>
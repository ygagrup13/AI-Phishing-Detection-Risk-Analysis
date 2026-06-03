<div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/scikit--learn-HistGB-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
<img src="https://img.shields.io/badge/Cloudflare-Browser%20Rendering-F38020?style=for-the-badge&logo=cloudflare&logoColor=white"/>
<img src="https://img.shields.io/badge/Accuracy-92.12%25-brightgreen?style=for-the-badge"/>
<img src="https://img.shields.io/badge/F1--Score-89.58%25-orange?style=for-the-badge"/>

# 🛡️ PhishGuard AI
### Yapay Zeka Destekli ve Çok Katmanlı Phishing Tespit & Risk Analizi Sistemi

> **Fırat Üniversitesi · Yazılım Mühendisliği Bölümü**  
> Yazılım Gereksinim Analizi Dersi — Grup Projesi

*"Bir linke tıklamadan önce düşünmek yerine, sistem düşünsün."*

</div>

---

## 📌 Proje Hakkında

**PhishGuard AI**, kullanıcıların şüpheli web sitelerini saniyeler içinde analiz edebilmesini sağlayan, **hibrit mimariye sahip** bir **phishing tespit ve risk analizi** sistemidir.

Geleneksel antivirüs yazılımları yalnızca bilinen phishing listelerini (kara listeler) tararken, PhishGuard AI hem **yapısal URL niteliklerini makine öğrenmesiyle (ML)** hem de **sayfa içeriğini (NLP/HTML)** kural tabanlı hibrit bir risk katmanıyla gerçek zamanlı olarak analiz ederek, kara liste tabanlı yöntemlere kıyasla daha önce görülmemiş phishing URL'lerini tespit edebilecek şekilde tasarlanmıştır.

### 🎯 Neden PhishGuard AI?

| Özellik | Geleneksel Çözümler | PhishGuard AI |
|--------|---------------------|---------------|
| Bilinmeyen saldırı tespiti | ❌ | ✅ |
| URL yapısal analizi | ❌ | ✅ (21 özellik) |
| NLP içerik analizi | ❌ | ✅ (11 özellik) |
| Typosquatting tespiti | ❌ | ✅ (35+ marka) |
| IDN/Punycode homoglif tespiti | ❌ | ✅ |
| JavaScript render desteği | ❌ | ✅ (Cloudflare API) |
| Gerçek zamanlı REST API | ❌ | ✅ |
| Türkçe phishing tespiti | ❌ | ✅ |

---

## 👥 Geliştirici Ekip & Proje Liderliği

### 👑 Project Leadership

**Meryem Tekeli – Project Lead & AI/ML Engineer**

Bu proje kapsamında genel sistem mimarisi, makine öğrenmesi modeli geliştirme süreci, hibrit risk skorlama mekanizması, performans değerlendirme çalışmaları ve kullanıcı arayüzü entegrasyonu koordine edilmiştir.

| İsim | Birincil Rol & Teknik Uzmanlık | Sorumluluk Alanları ve Modüller |
|------|-------------------------------|----------------------------------|
| **Meryem Tekeli** | Project Lead & AI/ML Engineer | `model/ml_model.py`, `model/train_v2.py`, `frontend/index.html` |
| **Zelal Ergin** | Scrum Master & Feature Engineering Lead | `features/url_features.py` |
| **Mehmet Polat Maç** | Web Crawling & Data Collection Engineer | `crawler/web_crawler.py` |
| **Muhammed Kayra Doğan** | NLP & Content Analysis Engineer | `features/text_features.py` |
---

## 🚀 Özellikler & Özellik Çıkarımı

Sistem, iki farklı modülden toplam **32 özellik (feature)** çıkarır. Ancak bu özelliklerin işlenme mantığı teknik olarak birbirinden farklıdır:
- **21 Adet URL Özelliği**: Doğrudan makine öğrenmesi modelinin (`HistGradientBoostingClassifier`) eğitiminde ve tahmin (inference) adımında kullanılır.
- **11 Adet NLP & HTML Özelliği**: Büyük veri setlerinde tarama (crawling) maliyetinin yüksek olması ve veride seyreklik (sparsity) yaratması sebebiyle model eğitimine dahil edilmemiştir. Bunun yerine, modelin ürettiği baz olasılık skorunu desteklemek amacıyla **tahmin sonrası kural tabanlı risk katmanında** değerlendirilir.

### 🔗 URL Analizi — 21 Özellik (ML Eğitimi ve Tahmininde Kullanılır)

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

### 🧠 NLP & HTML Analizi — 11 Özellik (Kural Tabanlı Risk Skorlama Katmanında Kullanılır)

| Özellik | Açıklama |
|---------|----------|
| `phishing_tfidf_weighted_score` | TF-IDF ağırlıklı phishing kelime skoru |
| `phishing_lexicon_mention_count` | 30+ phishing kelimesinin geçiş sayısı |
| `phishing_text_risk_0_100` | 0-100 normalize edilmiş metin risk skoru |
| `form_count` | `<form>` etiketi sayısı |
| `input_count` | `<input>` etiketi sayısı |
| `external_link_ratio` | Farklı domaine giden link oranı |
| `hidden_element_count` | `display:none` / `visibility:hidden` element sayısı |
| `favicon_foreign` | Favicon farklı domainden mi geliyor? |
| `urgency_score` | Aciliyet/manipülasyon ifadesi sayısı |
| `typo_ratio` | Yazım hatası oranı |
| `panic_score` | Panik/korku tonu skoru |

---

### 🎭 Gelişmiş Typosquatting & Homoglif Tespiti

35+ bilinen marka ile çok katmanlı benzerlik analizi gerçekleştirilir:

- **Leet-speak normalizasyonu**: `g00gle` → `google`, `paypa1` → `paypal`
- **Unicode homoglif haritalaması**: Kiril, Latin varyantları (`ı`, `а`, `е`, `о`, `р`, `с`, `х`, `у`)
- **IDN/Punycode çözme**: `xn--ncrosoft-tkb` → `mıcrosoft` → `microsoft`
- **SequenceMatcher**: %70+ benzerlik eşiği ile bulanık eşleşme analizi
- **Tire saldırısı**: `secure-login-paypal.xyz` → `paypal` markası tespit edilir
- **Resmi kısa domain koruması**: `youtu.be`, `t.co`, `fb.com` gibi resmi kısa domainlerin oluşturabileceği yanlış alarmlar engellenir

---

### 🌐 Çift Katmanlı Web Crawler

```
İstek Geldi
     │
     ▼
USE_CLOUDFLARE = True?
     │
     ├─ EVET → Cloudflare Browser Rendering API (Chrome Headless)
     │              (JavaScript render edilir)
     │              Başarısız olursa ↓
     └─ HAYIR / FALLBACK → BeautifulSoup Crawler
                               (Hızlı, SSL-bypass destekli)
```

**Cloudflare Browser Rendering API**: JavaScript ile dinamik yüklenen sayfaları (SPA, React, Vue) render ederek analiz sürecine dahil eder. BeautifulSoup tabanlı tarayıcılar yalnızca statik kaynak kodunu okuduğundan bu tür dinamik içerikleri analiz edemez.

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

Günümüz phishing siteleri çoğunlukla React, Vue veya Angular ile geliştirilmektedir. Geleneksel `requests + BeautifulSoup` yaklaşımı bu sayfalarda yalnızca boş bir `<div id="root">` görür; gerçek içerik JavaScript çalıştıktan sonra yüklenir. Cloudflare API bu sorunu çözmeyi amaçlar.

### Entegrasyon ve Güvenlik (.env Kullanımı)

Açık kaynak standartları gereği API kimlik bilgilerinin kod içerisine gömülmesi (hardcoded) güvenlik açığı oluşturur. Projede API anahtarlarının `.env` dosyası üzerinden yönetilmesi önerilir:

```python
# crawler/web_crawler.py
import os
from dotenv import load_dotenv

load_dotenv()
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN  = os.getenv("CLOUDFLARE_API_TOKEN")
```

---

## 📊 Sistem Mimarisi

Aşağıdaki şema, sistemin gerçek veri akışını ve modül sorumluluklarını göstermektedir:

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
          ┌───────────┴───────────┐
          ▼                       ▼
   ┌──────────────┐        ┌──────────────┐
   │ URL Özellik  │        │  Sayfa Metni │
   │  Çıkarıcı    │        │   & HTML     │
   │ (url_features)│       │ (web_crawler)│
   └──────┬───────┘        └──────┬───────┘
          │                       │
          │ 21 URL Özelliği       │ HTML/Text İçeriği
          ▼                       ▼
   ┌──────────────┐        ┌──────────────┐
   │   ML Model   │        │ NLP/HTML Öz. │
   │ (model_v2.pkl)│       │  Çıkarıcı    │
   │  [HistGB]    │        │(text_features)│
   └──────┬───────┘        └──────┬───────┘
          │                       │
          │ P(Phishing)           │ 11 NLP/HTML Özelliği
          ▼                       ▼
   ┌──────────────────────────────────────────────┐
   │         Kural Tabanlı Risk Düzeltici         │
   │           & Typosquatting Motoru             │
   │   (ML'den gelen base_risk üzerine ek/çıkarma  │
   │      risk puanı uygular ve etiketler)        │
   └──────────────────────┬───────────────────────┘
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

### Karşılaştırmalı Model Analizi (716K Veri Seti Üzerinde)

Modeller, veri setindeki seyreklik ve crawler zaman maliyeti nedeniyle **yalnızca 21 URL özelliği** kullanılarak eğitilmiştir.

| Model | CV F1 (5-fold) | Açıklama |
|-------|----------------|----------|
| Logistic Regression | 0.7663 (±0.0008) | Temel Doğrusal Sınıflandırıcı |
| Random Forest | 0.8959 (±0.0004) | Yüksek Başarımlı Ensemble |
| **HistGradientBoosting (Gradient Boosted Decision Trees)** ✅ | **0.8965 (±0.0003)** | **En İyi Performans Gösteren Model** |

### Seçilen Model: HistGradientBoosting — Test Seti Sonuçları

| Metrik | Değer | Açıklama |
|--------|-------|----------|
| **Accuracy** | **%92.12** | Genel Doğruluk Oranı |
| **F1 Score** | **%89.58** | Phishing Sınıfı F1 Skoru |
| **Precision** | **%93.47** | Phishing Olarak İşaretlenenlerin Doğruluğu |
| **Recall** | **%86.01** | Gerçek Phishing Sitelerini Yakalama Oranı |
| **False Positive Rate** | **%3.91** | Meşru Sitelerin Yanlışlıkla Engellenme Oranı (Çok Düşük) |

> **Eğitim Verisi**: 716.235 benzersiz URL (phishing + legitimate dengeli/ağırlıklı)  
> **Doğrulama**: 5-katlı çapraz doğrulama (Stratified Cross-Validation)

### Kullanılan Veri Setleri

| Dosya | Kaynak | Boyut | İçerik / Satır Sayısı |
|-------|--------|-------|--------|
| `phishing_site_urls.csv` | Kaggle — Phishing Site URLs | ~30 MB | URL + etiket (bad/good), 549,346 satır |
| `malicious_phish.csv` | Kaggle — Malicious URLs Dataset | ~43 MB | URL + etiket (phishing/benign/malware), 651,191 satır |
| `dataset_phishing.csv` | Kaggle — Web Page Phishing Detection | ~3.5 MB | URL + etiket (phishing/legitimate), 11,430 satır |
| `uci-ml-phishing-dataset.csv` | UCI Machine Learning Repository | ~824 KB | Klasik UCI phishing dataseti, 11,055 satır |

> 📦 **Toplam ham veri**: ~1.22M+ satır · **Eğitime katılan (duplicate temizlendi)**: **716.235** benzersiz URL

---

## 🧪 Test Sonuçları ve Senaryoları

| URL | Beklenen | Sonuç | Risk Skoru | Açıklama / Test Senaryosu |
|-----|----------|-------|------------|---------------------------|
| `https://www.google.com` | GÜVENLİ | ✅ LEGITIMATE | 5 | Gerçek Güvenli Site |
| `https://www.trendyol.com` | GÜVENLİ | ✅ LEGITIMATE | 19 | Gerçek Güvenli Site |
| `https://github.com` | GÜVENLİ | ✅ LEGITIMATE | 5 | Gerçek Güvenli Site |
| `https://youtu.be/Pt-TPo05fdI` | GÜVENLİ | ✅ LEGITIMATE | 5 | Whitelist / Kısa URL Kontrolü |
| `http://secure-login-paypal.xyz/update-account` | PHİSHİNG | ✅ PHISHING | 95 | Taklit Kelime & Güvensiz Protokol |
| `https://nicrosoft.com` | PHİSHİNG | ✅ PHISHING | 80 | Simüle Edilmiş Typosquatting (N-M Değişimi) |
| `https://paypa1.com` | PHİSHİNG | ✅ PHISHING | 65 | Simüle Edilmiş Typosquatting (Leet-speak) |
| `http://xn--mcrosoft-tkb.com` (mıcrosoft) | PHİSHİNG | ✅ PHISHING | 90 | Simüle Edilmiş Homoglif (IDN/Kiril) |
| `http://g00gle-verify.tk/signin` | PHİSHİNG | ✅ PHISHING | 98 | Çok Katmanlı Saldırı (Leet-speak + TLD) |

---

## 🔒 Güvenlik Katmanları

```
Katman 1: URL Format Doğrulama
  └── Protokol, domain yapısı, TLD minimum uzunluğu

Katman 2: Bilinen Güvenli Domain Bypass
  └── SAFE_DOMAINS listesi + YouTube oEmbed doğrulaması
  └── Eğitim/Devlet kurumu otomatik tanıma (.edu.tr, .gov.tr)

Katman 3: URL Yapısal Analizi (21 Feature)
  └── Entropi, şüpheli kelimeler, TLD, IP kullanımı...

Katman 4: NLP & HTML İçerik Analizi (11 Feature)
  └── TF-IDF, form sayısı, gizli elementler, aciliyet skoru...

Katman 5: Typosquatting & Homoglif Motoru
  └── Leet-speak + Unicode + IDN/Punycode + SequenceMatcher

Katman 6: HistGradientBoosting ML Tahmini
  └── 716K+ örnekle eğitilmiş, %92.12 accuracy (Sadece URL Özellikleri)

Katman 7: Kural Tabanlı Risk Düzeltici
  └── NLP sinyalleri + protokol typosquatting + trusted TLD indirimleri
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
│   │   ├── ml_model.py             # HistGradientBoosting + Typosquatting + Risk motoru
│   │   └── train_v2.py             # Model yeniden eğitim pipeline'ı
│   │
│   ├── frontend/
│   │   └── index.html              # Web arayüzü (Gauge, animasyonlar, risk kartları)
│   │
│   ├── data/
│   │   ├── rf_model.pkl            # Geriye dönük uyumluluk için korunan model dosyası (Legacy)
│   │   └── combined_dataset.csv    # Birleştirilmiş ve temizlenmiş dataset
│   │
│   ├── models/
│   │   └── model_v2.pkl            # HistGradientBoosting tabanlı v2 model dosyası (Ana model)
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
| **ML Engine** | HistGradientBoosting (scikit-learn) | Phishing sınıflandırması |
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

Açık kaynak standartları gereği kimlik bilgilerinin `.env` dosyasından okunması önerilir:

```python
# .env dosyası
CLOUDFLARE_ACCOUNT_ID="hesap-id"
CLOUDFLARE_API_TOKEN="cfut_token"
```

```python
# api.py içinde (satır 25)
USE_CLOUDFLARE = True   # Cloudflare Browser Rendering API aktif
USE_CLOUDFLARE = False  # Sadece BeautifulSoup kullan
```

### Model Versiyonu

Sistem önce `models/model_v2.pkl` (HistGradientBoosting pipeline), bulamazsa `data/rf_model.pkl` (legacy) yükler. İkisi de yoksa otomatik eğitim başlatır.

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
- `is_trusted_tld(url)` — `.edu.tr`, `.gov.tr` gibi güvenilir uzantıları tespit eder
- `URL_FEATURE_KEYS` — Modelin beklediği sıralı feature listesi

### `features/text_features.py`

- `extract_text_features(page_text, html)` — 11 NLP & HTML özelliği döndürür
- TF-IDF vektörleyici modül yüklenirken hazır corpus ile eğitilir (one-time)
- İngilizce + Türkçe 30+ phishing kelime sözlüğü
- E-ticaret whitelist: kampanya kelimelerinin oluşturabileceği yanlış alarmlar minimize edilir

### `model/ml_model.py` + `model/train_v2.py` *(Project Lead / AI & ML Development)*

Makine öğrenmesi pipeline tasarımı, veri ön işleme, model eğitimi ve risk skorlama sisteminin mimari bileşenleri:

| Bileşen | Teknik Açıklama ve Katkılar |
|---------|------------------------------|
| **Model Eğitimi** | 4 farklı CSV veri setini birleştirme, veri tekilleştirme, 716.235 benzersiz URL ve **21 URL özelliği** ile HistGradientBoosting eğitimi |
| **5-Fold Cross Validation** | Eğitim sırasında 5-katlı çapraz doğrulama (Stratified CV) ile model başarısının doğrulanması |
| **Risk Skoru (0-100)** | `LEGITIMATE` → `phishing_proba × 30` (max 30), `PHISHING` → `50 + phishing_proba × 50` (50-100) formülasyonu ile normalizasyon |
| **Güven Oranı** | Model `predict_proba()` çıktısı; frontend entegrasyonunda `LEGITIMATE` için `100 - risk_score`, `PHISHING` için `risk_score` olarak gösterim |
| **Kural Tabanlı Risk Düzeltici** | NLP sinyalleri (TF-IDF, form, hidden, urgency, panic) ek puan hesaplamaları; trusted TLD için -40 puan indirimi |
| **Risk Seviyesi Etiketleme** | `≤40` → Düşük, `41-70` → Orta, `>70` → Yüksek seviyeli etiketleme sistemi |
| **Typosquatting Motoru** | 7 katmanlı analiz: leet-speak, Unicode homoglif, IDN/Punycode çözümü, tire saldırısı, SequenceMatcher analizi |
| **Model Versiyonlama** | `model_v2.pkl` (HistGradientBoosting) → `rf_model.pkl` (legacy) öncelikli yükleme algoritması |
| `predict_phishing(feature_vector)` | Hibrit tahmin akışının yönetimi ve tüm güvenlik katmanlarının çalıştırılması |
| `train_and_save_model()` | Sıfırdan model eğitimi, çapraz doğrulama skorlarının hesaplanması ve joblib serileştirme |
| `_detect_suspicious(feature_vector)` | Özellikler için eşik tabanlı (threshold-based) şüpheli özellik tespiti |
| `is_local_or_private(url)` | Yerel ve özel IP adresleri için bypass algoritması |

### `api.py`

- `POST /analyze` — Ana analiz endpoint'i
- `GET /` — Web arayüzünü serve eder
- `is_known_safe_domain(url)` — Güvenli domain bypass + YouTube oEmbed doğrulama
- `validate_url(url)` — Sadece yapısal URL doğrulama (ağ isteği olmadan)

### `frontend/index.html` *(Frontend Geliştirme & UI/UX Tasarımı)*

Siber güvenlik temalı tek sayfalık web arayüzünün bileşenleri ve görsel arayüz mimarisi:

| Bileşen | Teknik Açıklama |
|---------|-----------------|
| **Animated Particle Network** | HTML5 Canvas üzerinde 80 dinamik parçacık ve aralarında bağlantı çizgileri; mor-mavi renk geçişli animasyon |
| **Glassmorphism Tasarım** | Modern `backdrop-filter: blur(20px)` stili ve mor renkli yarı şeffaf kart düzeni |
| **Orbitron + Inter Fontları** | Google Fonts üzerinden siber güvenlik ve teknoloji temalı tipografi entegrasyonu |
| **Risk Gauge (SVG Dairesel İlerleme)** | Risk skoru (0-100) animasyonlu dairesel SVG göstergesi; renk kodları: 🟢 Düşük / 🟡 Orta / 🔴 Yüksek |
| **Güven Oranı Gösterimi** | Analiz sonucuna göre: `LEGITIMATE` için `%{100 - risk_score} güvenli`, `PHISHING` için `%{risk_score} risk` gösterimi |
| **Analiz Animasyonu** | 6 adımlı sıralı durum animasyonu (tarayıcı → NLP → ML → sonuç adımları) |
| **Şüpheli Özellikler Kartı** | Tespit edilen şüpheli özellikler için Türkçe açıklamalı dinamik badge sistemi |
| **URL Bilgileri Tablosu** | Çözümlenen domain, protokol, dizin yolu ve URL uzunluğunun satır bazlı gösterimi |
| **Feature Analizi Kartı** | Çıkarılan ham özellik değerlerinin kullanıcı arayüzünde görsel olarak listelenmesi |
| **ERİŞİLEMEYEN Özel Ekranı** | Bağlantı kurulamayan web siteleri için gauge sıfırlayan, ikincil kartları gizleyen dinamik uyarı şablonu |
| **Hata Yönetim Kartı** | API bağlantısı koptuğunda kullanıcıya hata giderme adımlarını gösteren dinamik bildirim |
| **Responsive Grid Mimarisi** | 900px üzerindeki çözünürlüklerde 3 sütunlu yerleşim, mobil ekranlarda tek sütunlu esnek tasarım |

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

7. HistGradientBoosting ML Tahmini
   └─ P(phishing) → base_risk hesapla (Sadece 21 URL özelliği ile)

8. Kural Tabanlı Risk Düzeltici
   ├─ NLP sinyalleri ekle (TF-IDF, form, hidden, urgency, panic...)
   ├─ Yönlendirme ve protokol typosquatting kontrolleri
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

*716.235 URL · %92.12 Accuracy · 5-Fold Stratified CV · 21 ML + 11 Hibrit Özellik · Türkçe + İngilizce Destek*

</div>
# pyright: ignore
# type: ignore

# =============================================================================
# 🌐 URL Özellik Çıkarma Modülü
# Dosya: url_features.py
# Açıklama:
#   Bu modül, verilen bir URL'den phishing (oltalama) tespiti için
#   çeşitli yapısal ve içerik tabanlı özellikler çıkarır.
# =============================================================================

import re
import math
from urllib.parse import urlparse
from collections import Counter
import tldextract


# -----------------------------------------------------------------------------
# 🔢 Entropy (Düzensizlik) Hesaplama
# -----------------------------------------------------------------------------
def calculate_entropy(text: str) -> float:
    """
    Verilen metnin entropy (rastgelelik) değerini hesaplar.

    Args:
        text (str): Analiz edilecek metin

    Returns:
        float: Entropy değeri
    """
    if not text:
        return 0.0

    counter = Counter(text)
    probs = [count / len(text) for count in counter.values()]

    return -sum(p * math.log2(p) for p in probs)


# -----------------------------------------------------------------------------
# 🔍 URL Özelliklerini Çıkarma
# -----------------------------------------------------------------------------
def extract_url_features(url: str) -> dict:
    """
    Verilen URL'den phishing tespiti için özellikler çıkarır.

    Args:
        url (str): Analiz edilecek URL

    Returns:
        dict: Özellikler sözlüğü
    """

    # --- Temel ayrıştırma ---
    parsed_url = urlparse(url)
    ext = tldextract.extract(url)

    # --- IP adresi tespiti ---
    ip_pattern = r'(\d{1,3}\.){3}\d{1,3}'
    has_ip = 1 if re.search(ip_pattern, url) else 0

    # --- Domain parçaları ---
    subdomain = ext.subdomain
    domain = ext.domain
    tld = ext.suffix

    # IP varsa subdomain sayılmaz
    subdomain_count = 0 if has_ip else (
        len(subdomain.split('.')) if subdomain else 0
    )

    # --- Şüpheli kelimeler ---
    suspicious_words = [
        "login", "verify", "secure", "update", "account", "banking",
        "confirm", "password", "signin", "paypal", "ebay", "webscr",
        "cmd", "submit", "redirect", "click", "download", "free",
        "bonus", "winner", "urgent", "suspend", "limited", "expire",
        "alert", "customer", "support", "service"
    ]

    # --- URL kısaltma servisleri ---
    shortening_services = [
        "bit.ly", "tinyurl.com", "t.co", "goo.gl",
        "ow.ly", "is.gd", "buff.ly", "short.link"
    ]

    # --- Feature çıkarımı ---
    features = {
        "url_length": len(url),
        "has_https": 1 if parsed_url.scheme == "https" else 0,
        "has_at": 1 if "@" in url else 0,
        "dash_count": url.count("-"),
        "has_ip": has_ip,
        "subdomain_count": subdomain_count,
        "special_char_count": sum(url.count(c) for c in "?=&%#"),
        "has_port": 1 if parsed_url.port else 0,
        "digit_count": sum(c.isdigit() for c in url),
        "has_redirect": 1 if "//" in parsed_url.path else 0,
        "suspicious_keyword_count": sum(
            1 for word in suspicious_words if word in url.lower()
        ),
        "domain_length": len(domain),
        "is_suspicious_tld": 1 if tld in ["xyz", "tk", "ml", "ga", "cf"] else 0,
        "path_length": len(parsed_url.path),

        # --- Yeni eklenen özellikler ---
        "url_entropy": round(calculate_entropy(url), 4),
        "is_shortened": 1 if any(
            service in url.lower() for service in shortening_services
        ) else 0,
        "dot_count": url.count("."),
        "digit_ratio": round(
            sum(c.isdigit() for c in url) / len(url), 4
        ) if len(url) > 0 else 0,
        "has_double_extension": 1 if len(
            re.findall(r'\.(com|net|org|edu|gov|verify|secure)\.', url.lower())
        ) > 0 else 0,
        "https_in_domain": 1 if (
            "https" in domain.lower() or "https" in subdomain.lower()
        ) else 0,
    }

    return features


# -----------------------------------------------------------------------------
# 🧪 Test
# -----------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 📋 Sabit Feature İsimleri — ml_model.py tarafından import edilir
# ---------------------------------------------------------------------------
URL_FEATURE_KEYS = (
    "url_length",
    "has_https",
    "has_at",
    "dash_count",
    "has_ip",
    "subdomain_count",
    "special_char_count",
    "has_port",
    "digit_count",
    "has_redirect",
    "suspicious_keyword_count",
    "domain_length",
    "is_suspicious_tld",
    "path_length",
    "url_entropy",
    "is_shortened",
    "dot_count",
    "digit_ratio",
    "has_double_extension",
    "https_in_domain",
)


if __name__ == "__main__":
    test_url = "http://secure-login-bank123.xyz/verify/account"

    features = extract_url_features(test_url)

    print(f"Toplam {len(features)} özellik çıkarıldı:")
    for key, value in features.items():
        print(f"  {key}: {value}")

    print(f"\nURL_FEATURE_KEYS ({len(URL_FEATURE_KEYS)} adet):")
    print(URL_FEATURE_KEYS)

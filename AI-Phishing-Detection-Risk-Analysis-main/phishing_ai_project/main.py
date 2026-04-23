# pyright: ignore
# type: ignore

"""
Ana Çalıştırma Dosyası — Phishing Tespit Pipeline'ı
=====================================================
Akış:
    1. Kullanıcıdan URL al
    2. Crawler → (page_text, links, html)
    3. URL Feature Extraction
    4. Text/HTML Feature Extraction
    5. Feature birleştirme
    6. ML Model tahmini
    7. Güzel formatlı rapor
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from crawler.web_crawler import crawl_site
from features.url_features import extract_url_features
from features.text_features import extract_text_features
from model.ml_model import predict_phishing


# ---------------------------------------------------------------------------
# 🖨️ Formatlı Rapor Yazdırma
# ---------------------------------------------------------------------------
def _print_report(url: str, result: dict) -> None:
    label    = result["label"]
    risk     = result["risk_score"]
    level    = result["risk_level"]
    conf     = result["confidence"] * 100
    susp     = result["suspicious_features"]

    label_tr = "⚠  PHİSHİNG" if label.lower() == "phishing" else "✔  GÜVENLİ"

    W = 46  # kutu genişliği (iç)

    def row(text=""):
        return f"║ {text:<{W}} ║"

    sep = "╠" + "═" * (W + 2) + "╣"

    print()
    print("╔" + "═" * (W + 2) + "╗")
    print(row("  PHİSHİNG ANALİZ SONUCU"))
    print(sep)
    print(row(f"URL     : {url[:W - 10]}"))
    print(row(f"Etiket  : {label_tr}"))
    print(row(f"Risk    : {risk}/100  —  {level}"))
    print(row(f"Güven   : %{conf:.1f}"))
    print(sep)

    if susp:
        print(row("Şüpheli Özellikler:"))
        for feat in susp:
            print(row(f"  ⚠  {feat}"))
    else:
        print(row("Şüpheli özellik bulunamadı."))

    print("╚" + "═" * (W + 2) + "╝")
    print()


# ---------------------------------------------------------------------------
# 🏗️ Pipeline Adımları
# ---------------------------------------------------------------------------
def _step_crawl(url: str):
    try:
        page_text, links, html = crawl_site(url)
        return page_text or "", links or set(), html or ""
    except Exception as exc:
        print(f"[MAIN] Crawler hatası: {exc}")
        return "", set(), ""


def _step_url_features(url: str) -> dict:
    try:
        return extract_url_features(url)
    except Exception as exc:
        print(f"[MAIN] URL feature hatası: {exc}")
        return {}


def _step_text_features(page_text: str, html: str) -> dict:
    try:
        return extract_text_features(page_text, html)
    except Exception as exc:
        print(f"[MAIN] Text feature hatası: {exc}")
        return {}


def _step_predict(feature_vector: dict) -> dict:
    try:
        return predict_phishing(feature_vector)
    except Exception as exc:
        print(f"[MAIN] Tahmin hatası: {exc}")
        return {
            "label": "legitimate", "confidence": 0.0,
            "risk_score": 0, "risk_level": "Düşük",
            "suspicious_features": [],
        }


# ---------------------------------------------------------------------------
# 🚀 Ana Fonksiyon
# ---------------------------------------------------------------------------
def main(url: str = None) -> dict:
    print("=" * 50)
    print("  AI PHİSHİNG TESPİT SİSTEMİ — BAŞLADI")
    print("=" * 50)

    if url is None:
        print("\nLütfen analiz etmek istediğiniz URL'yi girin.")
        url = input("URL: ").strip()
        if not url:
            print("[MAIN] URL boş olamaz.")
            return {}

    if not url.startswith("http"):
        url = "http://" + url

    print(f"\n[MAIN] Analiz başlıyor → {url}\n")

    page_text, links, html = _step_crawl(url)
    url_feats = _step_url_features(url)
    text_feats = _step_text_features(page_text, html)

    feature_vector = {}
    feature_vector.update(url_feats)
    feature_vector.update(text_feats)

    result = _step_predict(feature_vector)
    _print_report(url, result)

    return result

if __name__ == "__main__":
    TEST_URL = "http://secure-login-paypal.xyz/update-account"
    main(url=TEST_URL)

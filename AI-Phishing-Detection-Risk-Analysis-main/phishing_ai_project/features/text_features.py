# pyright: ignore
# type: ignore

"""
Metin ve HTML Özellik Çıkarma Modülü (Text & HTML Feature Extractor)
======================================================================
Sorumlu : Zelal
Açıklama:
    Web sayfasından elde edilen ham metin ve HTML'yi işleyerek phishing
    tespiti için sayısal özellikler (features) üretir.

Çıkarılan özellikler (TEXT_FEATURE_KEYS sırasıyla):
    1. phishing_tfidf_weighted_score  — TF-IDF ağırlıklı phishing skoru
    2. phishing_lexicon_mention_count — Phishing kelime geçiş sayısı
    3. phishing_text_risk_0_100       — 0-100 normalize edilmiş risk skoru
    4. form_count                     — <form> tag sayısı
    5. input_count                    — <input> tag sayısı
    6. external_link_ratio            — Farklı domain'e giden link oranı
    7. hidden_element_count           — Gizli element sayısı
    8. favicon_foreign                — Favicon farklı domain'den mi (0/1)
"""

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------------------------------------------------------------------
# 🔑 Phishing Lexicon — EN + TR (30+ kelime)
# ---------------------------------------------------------------------------
PHISHING_LEXICON = [
    # İngilizce
    "login", "verify", "secure", "update", "account", "banking",
    "confirm", "password", "signin", "paypal", "ebay", "webscr",
    "cmd", "submit", "redirect", "urgent", "suspend", "limited",
    "expire", "alert", "blocked", "unauthorized", "credential",
    "click here", "free prize", "winner", "validate", "ssn",
    "social security", "credit card",
    # Türkçe
    "giriş", "şifre", "doğrula", "hesabınız", "askıya",
    "güvenlik", "ödeme", "kimlik", "parolanız", "doğrulama",
]

# ---------------------------------------------------------------------------
# 🤖 TF-IDF Vektörleyici — Modül yüklendiğinde eğitilir (one-time cost)
# ---------------------------------------------------------------------------
_PHISHING_CORPUS = [
    "login verify account password update",
    "secure banking confirm signin paypal ebay webscr",
    "cmd submit redirect urgent suspend limited expire",
    "alert blocked unauthorized credentials click here free prize",
    "giriş şifre doğrula hesabınız askıya güvenlik",
    "ödeme kimlik parolanız doğrulama kredi kartı",
]

_NORMAL_CORPUS = [
    "welcome home page services contact us",
    "privacy policy terms conditions about",
    "news blog articles products categories",
    "search results navigation footer header",
    "copyright reserved all rights information",
]

_TFIDF = TfidfVectorizer(ngram_range=(1, 2), max_features=300)
_TFIDF.fit(_PHISHING_CORPUS + _NORMAL_CORPUS)


# ---------------------------------------------------------------------------
# 🔧 Yardımcı Fonksiyonlar
# ---------------------------------------------------------------------------
def _tfidf_phishing_score(text: str) -> float:
    """
    Metni TF-IDF vektörüne çevirir ve phishing lexicon'u ile
    örtüşen terimlerin ağırlıklı toplamını döndürür.

    Args:
        text (str): Analiz edilecek metin

    Returns:
        float: Ağırlıklı phishing skoru
    """
    if not text or not text.strip():
        return 0.0
    try:
        vec = _TFIDF.transform([text[:10000]])
        feature_names = _TFIDF.get_feature_names_out()
        score = 0.0
        for idx, fname in enumerate(feature_names):
            if any(kw in fname for kw in PHISHING_LEXICON):
                score += vec[0, idx]
        return round(float(score), 4)
    except Exception:
        return 0.0


def _extract_base_domain(soup) -> str:
    """
    Sayfadaki ilk mutlak URL'den base domain'i çıkarır.

    Args:
        soup (BeautifulSoup): Parse edilmiş HTML

    Returns:
        str: Base domain veya boş string
    """
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if href.startswith("http"):
            return urlparse(href).netloc
    return ""


# ---------------------------------------------------------------------------
# 🏗️ Ana Özellik Çıkarma Fonksiyonu
# ---------------------------------------------------------------------------
def extract_text_features(page_text: str, html: str) -> dict:
    """
    Sayfa metni ve ham HTML'den phishing tespiti için 8 özellik çıkarır.

    Args:
        page_text (str): Crawler'dan gelen temizlenmiş metin
        html      (str): Sayfanın ham HTML içeriği

    Returns:
        dict: TEXT_FEATURE_KEYS ile tanımlı feature sözlüğü.
              Hata durumunda ilgili feature 0 değerini alır.
    """
    text_lower = (page_text or "").lower()

    # ── Metin Özellikleri ─────────────────────────────────────────────────
    phishing_tfidf_weighted_score = _tfidf_phishing_score(text_lower)

    phishing_lexicon_mention_count = sum(
        1 for kw in PHISHING_LEXICON if kw in text_lower
    )

    # 0-100 normalize: TF-IDF skoru * 15 + kelime sayısı * 4, max 100
    raw_risk = phishing_tfidf_weighted_score * 15 + phishing_lexicon_mention_count * 4
    phishing_text_risk_0_100 = round(min(raw_risk, 100.0), 2)

    # ── HTML Özellikleri ──────────────────────────────────────────────────
    form_count = 0
    input_count = 0
    external_link_ratio = 0.0
    hidden_element_count = 0
    favicon_foreign = 0

    if html:
        try:
            soup = BeautifulSoup(html, "html.parser")
            base_domain = _extract_base_domain(soup)

            # <form> ve <input> sayısı
            form_count = len(soup.find_all("form"))
            input_count = len(soup.find_all("input"))

            # Dış link oranı
            all_links = soup.find_all("a", href=True)
            if all_links:
                external = sum(
                    1 for a in all_links
                    if a["href"].startswith("http")
                    and base_domain
                    and urlparse(a["href"]).netloc != base_domain
                )
                external_link_ratio = round(external / len(all_links), 4)

            # Gizli elementler (display:none / visibility:hidden)
            hidden_pattern = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden")
            for tag in soup.find_all(True):
                style = tag.get("style", "").lower().replace(" ", "")
                if hidden_pattern.search(style):
                    hidden_element_count += 1

            # Favicon farklı domain'den mi?
            for link_tag in soup.find_all("link", rel=True):
                rel = link_tag.get("rel", [])
                if "icon" in rel or "shortcut icon" in rel:
                    href = link_tag.get("href", "")
                    if (
                        href.startswith("http")
                        and base_domain
                        and urlparse(href).netloc != base_domain
                    ):
                        favicon_foreign = 1
                    break

        except Exception as exc:
            print(f"[TEXT FEATURES] HTML parse hatası: {exc}")

    features = {
        "phishing_tfidf_weighted_score":  phishing_tfidf_weighted_score,
        "phishing_lexicon_mention_count": phishing_lexicon_mention_count,
        "phishing_text_risk_0_100":       phishing_text_risk_0_100,
        "form_count":                     form_count,
        "input_count":                    input_count,
        "external_link_ratio":            external_link_ratio,
        "hidden_element_count":           hidden_element_count,
        "favicon_foreign":                favicon_foreign,
    }

    print(
        f"[TEXT FEATURES] tfidf={phishing_tfidf_weighted_score:.3f} | "
        f"lexicon={phishing_lexicon_mention_count} | "
        f"risk={phishing_text_risk_0_100} | "
        f"form={form_count} | input={input_count}"
    )
    return features


# ---------------------------------------------------------------------------
# 📋 Sabit Feature İsimleri — ml_model.py tarafından import edilir
# ---------------------------------------------------------------------------
TEXT_FEATURE_KEYS = (
    "phishing_tfidf_weighted_score",
    "phishing_lexicon_mention_count",
    "phishing_text_risk_0_100",
    "form_count",
    "input_count",
    "external_link_ratio",
    "hidden_element_count",
    "favicon_foreign",
)


# ---------------------------------------------------------------------------
# 🧪 Test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    SAMPLE_HTML = """
    <html><body>
      <form action="http://evil-site.xyz/steal">
        <input type="text" name="username" placeholder="Enter your username"/>
        <input type="password" name="password" placeholder="Password"/>
        <input type="submit" value="Login"/>
      </form>
      <a href="http://evil-site.xyz/redirect">Click here to verify your account</a>
      <a href="https://google.com">Google</a>
      <div style="display:none">hidden trap</div>
      <link rel="icon" href="http://another-domain.com/icon.ico"/>
    </body></html>
    """
    SAMPLE_TEXT = (
        "Enter your password to verify your account. "
        "Your account has been suspended. Urgent action required. "
        "Click here to update your banking credentials."
    )

    result = extract_text_features(SAMPLE_TEXT, SAMPLE_HTML)
    print("\n── Text Feature Çıkarım Sonuçları ──")
    for k, v in result.items():
        print(f"  {k:40s}: {v}")

    print(f"\nTEXT_FEATURE_KEYS ({len(TEXT_FEATURE_KEYS)} adet):")
    print(TEXT_FEATURE_KEYS)

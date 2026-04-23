# =============================================================================
# 🧪 URL Özellik Çıkarma - Birim Testleri
# Dosya: test_url_features.py
# Açıklama:
#   Bu dosya, extract_url_features fonksiyonunu farklı senaryolarla test eder.
# =============================================================================

from url_features import extract_url_features


# -----------------------------------------------------------------------------
# 🌐 Test URL Listesi
# -----------------------------------------------------------------------------
test_urls = [
    # --- ✅ Güvenli URL Örnekleri ---
    "https://www.google.com",
    "https://www.github.com/settings/profile",
    "https://www.wikipedia.org",

    # --- ⚠️ Phishing URL Örnekleri ---
    "http://secure-login-paypal.xyz/update-account",
    "http://192.168.1.1/signin.php",
    "http://wellsfargo-verify-identity.ga/login",

    # --- 🚨 Kritik Senaryolar ---
    "https://bit.ly/3XyZ789",                 # Kısaltılmış URL
    "http://https-secure-login.com",          # Domain içinde HTTPS
    "http://paypal.com.verify.xyz/login"      # Çift uzantı
]


# -----------------------------------------------------------------------------
# 🚀 Test Çalıştırma
# -----------------------------------------------------------------------------
def run_tests():
    print("\n" + "=" * 60)
    print("PHISHING AI - URL ÖZELLİK ÇIKARIMI TESTLERİ")
    print("=" * 60)

    for url in test_urls:
        print(f"\n ANALİZ EDİLEN URL: {url}")
        print("-" * 60)

        try:
            results = extract_url_features(url)

            for key, value in results.items():
                print(f"  {key:.<30}: {value}")

        except Exception as e:
            print(f" HATA OLUŞTU: {e}")

        print("-" * 60)

    print("\n Test işlemi tamamlandı. Lütfen çıktıları kontrol et.")


# -----------------------------------------------------------------------------
# ▶️ Script çalıştırıldığında testleri başlat
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    run_tests()




import sys
import os

# Add project folder to path
sys.path.append(os.path.join(os.getcwd(), 'phishing_ai_project'))

from crawler.web_crawler import crawl_recursive

def main():
    # Test URL: Fırat Üniversitesi OBS (Akustik/Dinamik yapı testi)
    url = "https://obs.firat.edu.tr/"
    
    print(f"--- Gelişmiş Recursive Crawler Testi Başlatılıyor: {url} ---")
    
    # max_pages=5, max_depth=3 (Kullanıcı 3 olsun demişti)
    results = crawl_recursive(url, max_pages=5, max_depth=3)
    
    print(f"\n--- TEST SONUÇLARI ---")
    print(f"Toplam Taranan Sayfa: {len(results)}")
    
    for url, text in results.items():
        # İlk 30 karakteri ve uzunluğu göster
        snippet = text[:30].replace('\n', ' ')
        print(f"URL: {url} | Boyut: {len(text)} kr. | Özet: {snippet}...")

if __name__ == "__main__":
    main()

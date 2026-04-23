import sys
import os

# Add project folder to path
sys.path.append(os.path.join(os.getcwd(), 'phishing_ai_project'))

from crawler.web_crawler import crawl_recursive

def main():
    # Test URL: Fırat Üniversitesi OBS (Akustik/Dinamik yapı testi)
    url = "https://obs.firat.edu.tr/"
    
    print(f"--- Recursive Crawler Testi Başlatılıyor: {url} ---")
    
    # Maksimum 3 sayfa taranacak şekilde test edelim
    results = crawl_recursive(url, max_pages=3)
    
    print(f"\n--- TEST SONUÇLARI ---")
    print(f"Toplam Taranan Sayfa: {len(results)}")
    
    for url, text in results.items():
        print(f"URL: {url} | Metin Boyutu: {len(text)} karakter")

if __name__ == "__main__":
    main()

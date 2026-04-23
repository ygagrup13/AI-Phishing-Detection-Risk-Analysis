import sys
import os

# Add project folder to path
sys.path.append(os.path.join(os.getcwd(), 'phishing_ai_project'))

from crawler.web_crawler import crawl_site

def test_fast():
    url = "https://fast.com/tr/"
    print(f"\n--- Testing Fast.com (TR): {url} ---")
    html, text = crawl_site(url)
    
    if text:
        print(f"\n[SUCCESS] Extracted length: {len(text)} characters.")
        print("-" * 50)
        print(f"Burası çekilen metnin ilk 500 karakteridir:\n\n{text[:500]}...")
        print("-" * 50)
    else:
        print("[FAILED] Could not extract text from Fast.com.")

if __name__ == "__main__":
    test_fast()

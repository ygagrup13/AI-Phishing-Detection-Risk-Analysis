import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.getcwd(), 'phishing_ai_project'))

from crawler.web_crawler import crawl_site

def test_crawler():
    test_urls = [
        "https://www.google.com",
        "https://example.com",
        "https://thisisaveryinvalidurlthatshouldfail.com" # Should fail gracefully
    ]
    
    for url in test_urls:
        print(f"\n--- Testing: {url} ---")
        html_content, page_text = crawl_site(url)
        
        if page_text:
            print(f"Success! Extracted text length: {len(page_text)}")
            print(f"First 100 characters: {page_text[:100]}...")
        else:
            print("Failed or returned empty text.")

if __name__ == "__main__":
    test_crawler()

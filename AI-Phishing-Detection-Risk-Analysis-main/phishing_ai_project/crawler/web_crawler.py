# pyright: ignore
# type: ignore

import requests
from bs4 import BeautifulSoup
import re
import html
import os
from urllib.parse import urlparse, urljoin
import urllib3

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Sabit User-Agent (Bot engelleme için)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Taranmayacak dosya uzantıları
EXCLUDED_EXTENSIONS = {
    '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', # Görseller
    '.zip', '.rar', '.7z', '.tar', '.gz',                             # Arşivler
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',                   # Videolar
    '.mp3', '.wav', '.ogg', '.flac',                                  # Sesler
    '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt', '.csv'  # Dokümanlar
}

def clean_text(text):
    """
    Metni HTML gürültüsünden temizler, her etiketten sonra bir alt satıra geçer
    ve anlamsız kısa metinleri/gürültüleri filtreler.
    """
    if not text:
        return ""

    # HTML entity'leri normalize et (&nbsp; -> space vb.)
    text = html.unescape(text)
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Gereksiz boşlukları temizle
        line = re.sub(r'\s+', ' ', line).strip()
        
        # FİLTRELEME: 
        # 1. Boş değilse
        # 2. Sadece özel karakterlerden oluşmuyorsa
        # 3. Çok kısa değilse (örn. 2 karakterden az olan anlamsız satırlar)
        if line and not re.match(r'^[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ]+$', line):
            if len(line) > 1:
                cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def save_to_file(url, text, prefix=""):
    """
    Temizlenen metni bir .txt dosyasına kaydeder.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '_')
    path = parsed_url.path.replace('/', '_').strip('_')
    
    # Dosya adını güvenli hale getir
    safe_path = path if path else 'root'
    filename = f"{prefix}{domain}_{safe_path}.txt"
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'crawled_texts')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    file_path = os.path.join(output_dir, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"SOURCE URL: {url}\n")
            f.write("-" * 50 + "\n")
            f.write(text)
        print(f"[CRAWLER] İçerik kaydedildi: {file_path}")
        return file_path
    except Exception as e:
        print(f"[CRAWLER ERROR] Dosya kaydetme hatası: {e}")
        return None

def is_valid_url(url):
    """
    URL'nin taranabilir bir tipte (uzantıda) olup olmadığını kontrol eder.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()
    for ext in EXCLUDED_EXTENSIONS:
        if path.endswith(ext):
            return False
    return True

def crawl_site(url):
    """
    Verilen URL'den içeriği çeker, temizler ve içindeki linkleri bulur.
    
    Dönen Değerler:
    tuple: (cleaned_text, found_links)
    """
    found_links = set()
    try:
        print(f"[CRAWLER] '{url}' adresi taranıyor...")
        # verify=False ekleyerek SSL sertifika hatalarını es geçiyoruz (Bazı ünv. siteleri için)
        response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Gereksiz alanları temizle
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
            
        found_texts = []
        # Tüm div, p, a, h1-h3 etiketlerini tara
        for tag in soup.find_all(['div', 'p', 'a', 'h1', 'h2', 'h3']):
            if tag.name == 'a' and tag.has_attr('href'):
                link_url = tag['href']
                absolute_url = urljoin(url, link_url).split('#')[0]
                
                # Geçerli bir URL mi ve uzantısı uygun mu?
                if absolute_url.startswith('http') and is_valid_url(absolute_url):
                    found_links.add(absolute_url)
                
                link_text = tag.get_text(strip=True)
                if link_text:
                    found_texts.append(f"{link_text} -> [LINK: {absolute_url}]")
            else:
                tag_text = tag.get_text(separator=' ', strip=True)
                if tag_text:
                    found_texts.append(tag_text)
                    
        cleaned_text = clean_text('\n'.join(found_texts))
        return cleaned_text, found_links, response.text

    except Exception as e:
        print(f"[CRAWLER ERROR] '{url}' taranırken bir hata oluştu: {type(e).__name__}")
        return "", set(), ""

def crawl_recursive(start_url, max_pages=5, max_depth=3):
    """
    Başlangıç URL'sinden itibaren alt sayfaları derinlik takibi ile tarar.
    """
    parsed_start = urlparse(start_url)
    domain = parsed_start.netloc
    
    # Kuyruk yapısı: (URL, Mevcut Derinlik)
    to_visit = [(start_url, 0)]
    visited = set()
    visited_queued = {start_url} # Kuyruğa eklenenleri O(1) hızında kontrol etmek için
    all_results = {} # url -> text
    
    print(f"\n[RECURSIVE CRAWLER] Başlatıldı: {start_url} (Limit: {max_pages} sayfa, Derinlik: {max_depth})")
    
    while to_visit and len(visited) < max_pages:
        try:
            current_url, current_depth = to_visit.pop(0)
            
            if current_url in visited or current_depth > max_depth:
                continue
                
            # Sadece aynı domain ise ilerle (veya başlangıç URL'si ise)
            if urlparse(current_url).netloc != domain:
                continue
                
            # crawl_site her durumda linkleri dönmeli (boş sayfa fix)
            text, links = crawl_site(current_url)
            visited.add(current_url)
            
            # Bulunan metni kaydet
            if text:
                all_results[current_url] = text
                save_to_file(current_url, text, prefix="sub_")
            
            # Metin olsun olmasın linkleri sıraya ekle (Derinlik sınırına takılmıyorsa)
            if current_depth < max_depth:
                for link in links:
                    if urlparse(link).netloc == domain and link not in visited and link not in visited_queued:
                        to_visit.append((link, current_depth + 1))
                        visited_queued.add(link)
                            
        except Exception as e:
            print(f"[RECURSIVE ERROR] Beklenmedik döngü hatası: {e}")
            continue
        
    # Tüm sonuçları birleştirip tek bir ana dosya oluştur
    if all_results:
        combined_text = ""
        for url, text in all_results.items():
            combined_text += f"\n\n{'='*60}\nURL: {url}\n{'='*60}\n\n{text}"
            
        combined_path = save_to_file(start_url, combined_text, prefix="COMPLETE_")
        print(f"\n[SUCCESS] Tarama tamamlandı. Toplam {len(visited)} sayfa {max_depth} derinlikte taranıp {combined_path} dosyasına birleştirildi.")
        
    return all_results

def crawl_multiple_sites(urls):
    """
    Verilen URL listesini dolaşır ve her birini recursive olarak tarar.
    """
    results = []
    for url in urls:
        try:
            res = crawl_recursive(url)
            results.append((url, res))
        except Exception as e:
            print(f"[CRAWL MULTIPLE ERROR] '{url}' kümesi taranırken hata: {e}")
            continue
    return results

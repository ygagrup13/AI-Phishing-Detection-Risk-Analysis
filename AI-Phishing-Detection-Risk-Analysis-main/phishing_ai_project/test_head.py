from api import is_known_safe_domain

urls = [
    'https://youtu.be/ReGbqAB',
    'https://youtu.be/Pt-TPo05fdI'
]

for url in urls:
    res = is_known_safe_domain(url)
    print(f"URL: {url} -> Safe Domain: {res}")

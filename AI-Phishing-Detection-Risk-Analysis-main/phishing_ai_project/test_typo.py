"""
Typosquatting tespit testi — tüm kritik vakalar
"""
from urllib.parse import urlparse
from difflib import SequenceMatcher
import unicodedata, re as _re

LEET = {'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '6': 'b', '8': 'g', '@': 'a'}
HOMOGLYPHS = {
    '\u0131': 'i',  # ı (Turkish dotless i)
    '\u0456': 'i',  # Cyrillic і
    '\u0430': 'a',  # Cyrillic а
    '\u0435': 'e',  # Cyrillic е
    '\u043e': 'o',  # Cyrillic о
    '\u0440': 'r',  # Cyrillic р
    '\u0441': 'c',  # Cyrillic с
    '\u0445': 'x',  # Cyrillic х
    '\u0443': 'y',  # Cyrillic у
    '\u00e0': 'a', '\u00e1': 'a', '\u00e2': 'a', '\u00e4': 'a',
    '\u00e8': 'e', '\u00e9': 'e', '\u00ea': 'e', '\u00eb': 'e',
    '\u00ec': 'i', '\u00ed': 'i', '\u00ee': 'i', '\u00ef': 'i',
    '\u00f2': 'o', '\u00f3': 'o', '\u00f4': 'o', '\u00f6': 'o',
    '\u00f9': 'u', '\u00fa': 'u', '\u00fb': 'u', '\u00fc': 'u',
    '\u00f1': 'n', '\u00e7': 'c',
}

def normalize(s): return ''.join(LEET.get(c, c) for c in s)

def to_ascii_safe(s):
    result = []
    for c in s:
        if ord(c) < 128:
            result.append(c)
        elif c in HOMOGLYPHS:
            result.append(HOMOGLYPHS[c])
        else:
            decomposed = unicodedata.normalize('NFD', c)
            for dc in decomposed:
                if unicodedata.category(dc) != 'Mn' and ord(dc) < 128:
                    result.append(dc)
    return ''.join(result)

BRANDS = ['google', 'microsoft', 'apple', 'amazon', 'facebook', 'paypal',
          'netflix', 'youtube', 'linkedin', 'instagram', 'twitter']

TESTS = [
    # (url, expected_result_hint)
    ('https://xn--mcrosoft-tkb.com/',  'PHISHING — mıcrosoft IDN homoglyph'),
    ('https://microsoFt.com',          'PHISHING — case mismatch (if flagged)'),
    ('https://nicrosoft.com',          'PHISHING — nicrosoft ~ microsoft'),
    ('https://g00gle.com',             'PHISHING — leet substitution'),
    ('http://secure-login-paypal.xyz', 'PHISHING — paypal in dash domain'),
    ('http://paypa1.com',              'PHISHING — paypa1 ratio'),
    ('https://www.google.com',         'SAFE — real google'),
    ('https://www.microsoft.com',      'SAFE — real microsoft'),
    ('https://www.paypal.com',         'SAFE — real paypal'),
]

print('=' * 70)
for url, expected in TESTS:
    hostname = urlparse(url).hostname or ''
    domain = hostname.replace('www.', '').split('.')[0].lower()
    domain_norm = normalize(domain)
    domain_nodash = domain.replace('-', '')
    domain_nodash_norm = normalize(domain_nodash)

    idn_domain = domain
    if domain.startswith('xn--'):
        try:
            decoded = domain.encode('ascii').decode('idna')
            idn_domain = to_ascii_safe(decoded) or domain
            print(f'  [IDN] {domain} → decoded={decoded!r} → ascii={idn_domain!r}')
        except Exception as e:
            m = _re.match(r'^xn--(.+)-[a-z0-9]{2,4}$', domain)
            idn_domain = m.group(1) if m else domain
            print(f'  [IDN fallback] {domain} → {idn_domain} (err: {e})')

    idn_norm = normalize(idn_domain)
    idn_nodash = idn_domain.replace('-', '')
    idn_nodash_norm = normalize(idn_nodash)

    result = 'CLEAN'
    for brand in BRANDS:
        found = False
        for d_exact in (domain, domain_norm, idn_domain, idn_norm):
            if d_exact == brand:
                if domain == brand:
                    result = f'SAFE (exact: {brand})'; found = True; break
                result = f'PHISHING typosquat exact ({d_exact} == {brand})'; found = True; break
        if found: break
        if len(brand) >= 4:
            for nd in (domain_nodash, domain_nodash_norm, idn_nodash, idn_nodash_norm):
                if brand in nd and '-' in domain:
                    result = f'PHISHING dash-brand ({brand} in {nd})'; found = True; break
        if found: break
        for d in (domain, domain_norm, idn_domain, idn_norm):
            r = SequenceMatcher(None, d, brand).ratio()
            if 0.70 <= r < 1.0:
                result = f'PHISHING ratio={r:.2f} ({d!r} ~ {brand})'; found = True; break
        if found: break

    status = '✓' if (result.startswith('PHISHING') == expected.startswith('PHISHING')) else '✗ YANLIŞ'
    print(f'[{status}] {url}')
    print(f'       Beklenen: {expected}')
    print(f'       Sonuç   : {result}')
    print()

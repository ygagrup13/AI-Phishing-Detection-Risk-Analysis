import sys
sys.path.append('c:/Users/MSI/Downloads/AI-Phishing-Detection-Risk-Analysis-main/AI-Phishing-Detection-Risk-Analysis-main/phishing_ai_project')
from api import analyze_url, AnalyzeRequest

urls = [
    'https://microsoft.com',
    'https://nicrosoft.com',
    'https://paypa1.com',
    'https://trendyol.com',
    'https://secure-login-paypal.xyz'
]

for u in urls:
    print(f'Testing {u}...')
    try:
        req = AnalyzeRequest(url=u)
        res = analyze_url(req)
        print(f'  Label: {res.label}')
        print(f'  Risk Score: {res.risk_score} ({res.risk_level})')
        w = res.model_dump().get('warning') if hasattr(res, 'model_dump') else None
        if not w and hasattr(res, 'model_extra') and res.model_extra:
            w = res.model_extra.get('warning')
        if not w and hasattr(res, '__dict__'):
            w = res.__dict__.get('warning')
        print(f'  Warning: {w}')
        print(f'  Suspicious Features: {res.suspicious_features}')
    except Exception as e:
        print(f'  Error: {e}')
    print('-'*40)

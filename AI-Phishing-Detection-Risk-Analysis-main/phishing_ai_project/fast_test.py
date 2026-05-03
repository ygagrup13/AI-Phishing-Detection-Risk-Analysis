import sys
sys.path.append('c:/Users/MSI/Downloads/AI-Phishing-Detection-Risk-Analysis-main/AI-Phishing-Detection-Risk-Analysis-main/phishing_ai_project')

from features.url_features import extract_url_features
from model.ml_model import predict_phishing

urls = [
    'https://microsoft.com',
    'https://nicrosoft.com',
    'https://paypa1.com',
    'https://trendyol.com',
    'https://secure-login-paypal.xyz'
]

for u in urls:
    print(f'Testing {u}...')
    url_feats = extract_url_features(u)
    feature_vector = {}
    feature_vector.update(url_feats)
    feature_vector["_url"] = u
    
    res = predict_phishing(feature_vector)
    
    print(f'  Label: {res["label"]}')
    print(f'  Risk Score: {res["risk_score"]} ({res["risk_level"]})')
    w = res.get('warning')
    print(f'  Warning: {w}')
    print(f'  Suspicious Features: {res["suspicious_features"]}')
    print('-'*40)

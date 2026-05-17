from features.url_features import extract_url_features
from model.ml_model import predict_phishing
from api import is_known_safe_domain

urls = [
    "https://jasig.firat.edu.tr/cas/login?service=https://obs.firat.edu.tr",
    "http://secure-login-paypal.xyz",
    "https://gov.tr"
]

for url in urls:
    print(f"Testing: {url}")
    if is_known_safe_domain(url):
        print("  -> is_known_safe_domain: True")
    else:
        feats = extract_url_features(url)
        feats['_url'] = url
        res = predict_phishing(feats)
        print(f"  -> predict_phishing: {res['label']} (Risk: {res['risk_score']})")

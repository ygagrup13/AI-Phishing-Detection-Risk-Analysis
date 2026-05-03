import json
import urllib.request
import urllib.error

urls_to_test = [
    "https://www.google.com",
    "https://www.trendyol.com",
    "https://www.hepsiburada.com",
    "http://secure-login-paypal.xyz/update-account",
    "https://nicrosoft.com"
]

url_api = "http://127.0.0.1:8000/analyze"

for test_url in urls_to_test:
    data = json.dumps({"url": test_url}).encode("utf-8")
    req = urllib.request.Request(url_api, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(f"URL: {test_url}")
            print(f"Risk Score: {result.get('risk_score')}")
            print(f"Risk Level: {result.get('risk_level')}")
            print(f"Label: {result.get('label')}")
            print(f"Warning: {result.get('warning')}")
            print("-" * 40)
    except urllib.error.URLError as e:
        print(f"Error testing {test_url}: {e}")

import requests

def test_oembed(url):
    try:
        api_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        response = requests.get(api_url, timeout=5, verify=False)
        print(f"{url} oembed status: {response.status_code}")
    except Exception as e:
        print(f"Error for {url}: {e}")

test_oembed('https://youtu.be/ReGbqAB')
test_oembed('https://youtu.be/Pt-TPo05fdI')

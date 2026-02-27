import urllib.request
import urllib.parse
import json

url = 'http://127.0.0.1:8000/v1/recommend'

def run_test(gender):
    import urllib.request, urllib.parse, json
    data = {'request_json': f'{{"user_id":"test_u", "occasion":"party", "style_preferences":["streetwear"], "gender":"{gender}"}}'}
    # Encode as multipart form data is hard in pure urllib, but x-www-form-urlencoded might work for Form() strings
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode('utf-8'))
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode())
            outfits = res.get('outfits', [])
            genders = [o.get('outfit', {}).get('gender') for o in outfits]
            print(f"{gender.upper()} REQUEST GENDERS: {genders}")
    except urllib.error.HTTPError as e:
        print(f"Error for {gender}: {e.code} {e.reason}")
        print(e.read().decode())
    except Exception as e:
        print(f"Error for {gender}: {e}")

run_test('male')
run_test('female')

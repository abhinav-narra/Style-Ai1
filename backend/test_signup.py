import urllib.request
import urllib.parse
import json
import time

url = 'http://127.0.0.1:8000/v1/auth/signup'
data = {'email':'berunadh2@gmail.com', 'password':'mypassword', 'display_name': 'Test', 'gender': 'male'}
encoded_data = json.dumps(data).encode('utf-8')

req = urllib.request.Request(url, data=encoded_data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
         print(f"Success: {resp.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} {e.reason}")
    print(f"Body: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")

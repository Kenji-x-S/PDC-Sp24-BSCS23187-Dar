import requests
import time

API_URL = "http://127.0.0.1:8000/api/generate-challenge"

payload = {
    "difficulty": "easy"
}

print("Starting Circuit Breaker Test...\n")

for i in range(5):
    print(f"--- Request {i+1} ---")
    try:
        response = requests.post(API_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json().get('detail')}")
        
        print(f"Student Header: {response.headers.get('X-Student-ID')}\n")
    except Exception as e:
        print("Connection failed.\n")
    
    time.sleep(1)
import requests

url = "http://127.0.0.1:8000/auth/login"
data = {
    "username": "test@example.com",
    "password": "password123",
    "grant_type": "password"
}

try:
    # Register first
    reg_url = "http://127.0.0.1:8000/auth/register/start"
    print(f"Sending Registration to {reg_url}...")
    requests.post(reg_url, json={"email": "test@example.com", "password": "password123"})
    
    print(f"Sending POST to {url}...")
    response = requests.post(url, data=data)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")

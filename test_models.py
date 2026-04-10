import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

# Bu URL sana kullanabileceğin TÜM modelleri döner
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

res = requests.get(url)
if res.status_code == 200:
    models = res.json().get('models', [])
    print("--- Kullanabileceğin Modeller ---")
    for m in models:
        print(f"Model: {m['name']} | Versiyon: {m['version']}")
else:
    print(f"Modeller listelenemedi: {res.status_code} - {res.text}")
# chainalysis_client.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CHAINALYSIS_API_KEY = os.getenv("CHAINALYSIS_API_KEY")
BASE_URL = "https://public.chainalysis.com/api/v1/sanctions/address"

def chainalysis_check(address: str) -> dict:
    if not CHAINALYSIS_API_KEY:
        return {"error": "CHAINALYSIS_API_KEY not set (use .env)"}

    url = f"{BASE_URL}/{address}"

    headers = {
        "Token": CHAINALYSIS_API_KEY,
        "Accept": "application/json"
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

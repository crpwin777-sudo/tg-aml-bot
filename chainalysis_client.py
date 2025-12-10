# chainalysis_client.py
import os
import requests
from dotenv import load_dotenv
load_dotenv()

CHAINALYSIS_API_URL = os.getenv("CHAINALYSIS_API_URL")
CHAINALYSIS_API_KEY = os.getenv("CHAINALYSIS_API_KEY")

def chainalysis_check(address: str) -> dict:
    if not CHAINALYSIS_API_URL or not CHAINALYSIS_API_KEY:
        return {"error": "Chainalysis credentials not set (use .env)"}
    
    headers = {
        "X-API-KEY": CHAINALYSIS_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {"address": address}
    
    try:
        r = requests.post(
            CHAINALYSIS_API_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


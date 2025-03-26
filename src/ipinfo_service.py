from dotenv import load_dotenv
import os
import requests

# In case the env file is different than .env, specify it here
# load_dotenv("path/to/env/file")
load_dotenv()

token = os.getenv("IPINFO_TOKEN")

def get_location_from_ip(ip: str) -> dict:
    url = f"https://ipinfo.io/{ip}/json?token={token}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "loc": data.get("loc"),
            "provider": data.get("org")
        }
    else:
        return {"error": response.json()}
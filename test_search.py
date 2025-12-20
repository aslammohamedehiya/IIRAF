import requests
import json

try:
    resp = requests.post(
        "http://localhost:8000/api/search",
        json={"query": "vpn issue"}
    )
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2))
        
        # Check if resolution key exists in incidents
        incidents = [r for r in data['results'] if r['type'] == 'incident']
        if incidents:
            print(f"First incident resolution: '{incidents[0].get('resolution')}'")
        else:
            print("No incidents found in results.")
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"Request failed: {e}")

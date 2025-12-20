import requests
import json

# Test with a query that should match KB articles
queries = ["vpn troubleshooting", "password reset", "outlook sync"]

for query in queries:
    print(f"\n=== Testing: {query} ===")
    resp = requests.post(
        "http://localhost:8000/api/search",
        json={"query": query}
    )
    if resp.status_code == 200:
        data = resp.json()
        for r in data['results'][:3]:
            print(f"{r['type'].upper()}: {r['id']} - Score: {r['score']:.2f}")
            if r['type'] == 'kb':
                print(f"  Content: {r['content'][:60]}...")
            else:
                print(f"  Resolution: {r['resolution']}")
    else:
        print(f"Error: {resp.status_code}")

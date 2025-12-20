import requests
import json

# Test various queries to see KB article distribution
test_queries = [
    "vpn connection failed",
    "password reset",
    "email sync issue",
    "outlook not working",
    "printer setup",
    "slow performance",
    "login problem"
]

print("Testing KB Article Retrieval Across Different Queries")
print("="*60)

for query in test_queries:
    resp = requests.post(
        "http://localhost:8000/api/search",
        json={"query": query}
    )
    
    if resp.status_code == 200:
        data = resp.json()
        results = data['results']
        
        kb_count = sum(1 for r in results if r['type'] == 'kb')
        inc_count = sum(1 for r in results if r['type'] == 'incident')
        
        print(f"\nQuery: '{query}'")
        print(f"   Total: {len(results)} | KB: {kb_count} | Incidents: {inc_count}")
        
        # Show first 3 results
        for i, r in enumerate(results[:3], 1):
            type_label = "KB" if r['type'] == 'kb' else "INC"
            print(f"   {i}. [{type_label}] {r['id']} (score: {r['score']:.3f})")
    else:
        print(f"Error for '{query}': {resp.status_code}")

print("\n" + "="*60)

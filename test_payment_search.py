"""Test payment search functionality"""
from src.query_retrieval import QueryRetriever

qr = QueryRetriever()
results = qr.search("payment not successful", k=10)

print(f"\n{'='*80}")
print(f"Search Results for: 'payment not successful'")
print(f"{'='*80}\n")

for i, result in enumerate(results, 1):
    print(f"\n--- Result {i} ---")
    print(f"Type: {result['type']}")
    print(f"ID: {result['id']}")
    print(f"Score: {result['score']:.4f}")
    
    if result['type'] == 'incident':
        print(f"Text: {result['text'][:200]}...")
        print(f"Resolution: {result['resolution'][:200] if result['resolution'] else 'N/A'}...")
    else:  # KB article
        print(f"Title: {result['title']}")
        print(f"Content: {result['content'][:200]}...")

print(f"\n{'='*80}\n")

# Test the mapped KB articles
incident_ids = [r['id'] for r in results if r['type'] == 'incident']
print(f"\nIncident IDs found: {incident_ids}")

mapped_kbs = qr.get_mapped_kb_articles(incident_ids)
print(f"\nMapped KB articles: {len(mapped_kbs)}")

for kb in mapped_kbs:
    print(f"\n--- Mapped KB ---")
    print(f"ID: {kb['id']}")
    print(f"Title: {kb['title']}")
    print(f"Application: {kb['application']}")

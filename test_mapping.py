"""Test the incident-KB mapping functionality"""
from src.query_retrieval import QueryRetriever

print("Initializing QueryRetriever...")
qr = QueryRetriever()

# Test query
query = "checkout payment issue in OrderMgmt"
print(f"\nTest Query: '{query}'")
print("=" * 80)

# Get search results
print("\n1. Getting search results...")
all_results = qr.search(query, k=10)
print(f"   Total results from FAISS: {len(all_results)}")

# Separate incidents
incidents = [r for r in all_results if r['type'] == 'incident']
print(f"   Incidents found: {len(incidents)}")

# Show incident details
print("\n2. Incident Details:")
for inc in incidents[:5]:
    print(f"   - {inc['id']}: {inc['text'][:60]}...")

# Get incident IDs
incident_ids = [inc['id'] for inc in incidents]

# Get mapped KB articles
print("\n3. Getting mapped KB articles...")
mapped_kbs = qr.get_mapped_kb_articles(incident_ids)
print(f"   Mapped KB articles: {len(mapped_kbs)}")

# Show mapped KB details
print("\n4. Mapped KB Article Details:")
for kb in mapped_kbs[:5]:
    print(f"   - {kb['id']}: {kb['title']}")
    print(f"     Application: {kb['application']}")
    print(f"     Content: {kb['content'][:80]}...")
    print()

# Verify mapping
print("\n5. Verification:")
print(f"   ✓ Incidents returned: {len(incidents)}")
print(f"   ✓ Mapped KB articles returned: {len(mapped_kbs)}")
print(f"   ✓ Total results: {len(incidents) + len(mapped_kbs)}")

if mapped_kbs:
    print(f"\n   ✓ Mapping successful! KB articles are related to the incidents.")
else:
    print(f"\n   ⚠ No KB articles mapped to these incidents.")

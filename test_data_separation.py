from src.query_retrieval import QueryRetriever

qr = QueryRetriever()
results = qr.search('checkout payment issue', k=10)

print(f'Total results: {len(results)}')

incidents = [r for r in results if r['type'] == 'incident']
kbs = [r for r in results if r['type'] == 'kb']

print(f'Incidents: {len(incidents)}')
print(f'KB Articles: {len(kbs)}')

print('\nIncident samples:')
for r in incidents[:3]:
    print(f"  {r['id']}: {r['text'][:60]}...")

print('\nKB Article samples:')
for r in kbs[:3]:
    print(f"  {r['id']}: {r.get('title', 'N/A')} - {r['content'][:60]}...")

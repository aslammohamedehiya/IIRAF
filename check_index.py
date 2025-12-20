import pickle

# Check index composition
with open('index_store/iiraf_meta.pkl', 'rb') as f:
    meta = pickle.load(f)

kb_items = [m for m in meta if m['type'] == 'kb']
inc_items = [m for m in meta if m['type'] == 'incident']

print(f"Total items in index: {len(meta)}")
print(f"KB articles: {len(kb_items)}")
print(f"Incidents: {len(inc_items)}")
print(f"\nKB to Incident ratio: 1:{len(inc_items)//len(kb_items) if kb_items else 0}")

print("\n" + "="*60)
print("KB Articles in Index:")
print("="*60)
for item in kb_items:
    print(f"  {item['id']}: {item['title']}")
    print(f"    Content: {item['content'][:60]}...")
    print()

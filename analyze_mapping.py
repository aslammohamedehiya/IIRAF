import pandas as pd

# Load data
incidents = pd.read_csv(r'data\incidents.csv')
kb_articles = pd.read_csv(r'data\kb_articles.csv')

print("=== INCIDENTS ===")
print(f"Total incidents: {len(incidents)}")
print(f"\nApplications in incidents: {incidents['application'].unique()}")
print(f"\nRoot causes (first 10): {incidents['root_cause'].unique()[:10]}")
print(f"\nResolutions (first 5): {incidents['resolution'].unique()[:5]}")

print("\n=== KB ARTICLES ===")
print(f"Total KB articles: {len(kb_articles)}")
print(f"\nApplications in KB: {kb_articles['application'].unique()}")
print(f"\nTitles: {kb_articles['title'].tolist()}")

print("\n=== MAPPING ANALYSIS ===")
# Check if there's overlap in applications
incident_apps = set(incidents['application'].unique())
kb_apps = set(kb_articles['application'].unique())
print(f"Common applications: {incident_apps.intersection(kb_apps)}")
print(f"Incidents-only apps: {incident_apps - kb_apps}")
print(f"KB-only apps: {kb_apps - incident_apps}")

# Analyze root causes and KB content for mapping
print("\n=== ROOT CAUSE TO KB MAPPING ===")
for idx, kb in kb_articles.iterrows():
    print(f"\n{kb['kb_id']} ({kb['application']}): {kb['title']}")
    # Find incidents with similar root causes or resolutions
    matching = incidents[
        (incidents['application'] == kb['application']) |
        (incidents['root_cause'].str.contains(kb['application'], case=False, na=False))
    ]
    print(f"  Potential matching incidents: {len(matching)}")

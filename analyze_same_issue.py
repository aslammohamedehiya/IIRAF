import pandas as pd

# Load incidents
df = pd.read_csv('data/incidents.csv')

print("=" * 80)
print("ANALYZING: Same Issue Described in Different Words")
print("=" * 80)

# Example 1: Payments + Schema mismatch in payload
print("\n### Example 1: Payments Module - Schema Mismatch Issues ###\n")
payments_schema = df[(df['application'] == 'Payments') & (df['root_cause'] == 'Schema mismatch in payload')]
print(f"Found {len(payments_schema)} incidents with same root cause\n")

for idx, row in payments_schema.head(5).iterrows():
    print(f"ID: {row['incident_id']}")
    print(f"Summary: {row['issue_summary']}")
    print(f"Description: {row['issue_description'][:150]}...")
    print()

# Example 2: Login + Stale cache
print("\n### Example 2: Login Module - Stale Cache Issues ###\n")
login_cache = df[(df['application'] == 'Login') & (df['root_cause'] == 'Stale cache entry after deployment')]
print(f"Found {len(login_cache)} incidents with same root cause\n")

for idx, row in login_cache.head(3).iterrows():
    print(f"ID: {row['incident_id']}")
    print(f"Summary: {row['issue_summary']}")
    print()

# Example 3: Different modules, same root cause
print("\n### Example 3: Different Wordings Across Modules ###\n")
schema_issues = df[df['root_cause'] == 'Schema mismatch in payload']
print(f"Total incidents with 'Schema mismatch in payload': {len(schema_issues)}")
print(f"Across applications: {schema_issues['application'].unique()}")
print("\nDifferent issue summaries for same root cause:")
for summary in schema_issues['issue_summary'].unique()[:5]:
    print(f"  - {summary}")

print("\n" + "=" * 80)
print("CONCLUSION: Yes! Same issues are described with different wordings")
print("=" * 80)

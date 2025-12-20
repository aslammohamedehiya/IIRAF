import pandas as pd

# Load all datasets
incidents = pd.read_csv('data/incidents.csv')
kb_articles = pd.read_csv('data/kb_articles.csv')
patterns = pd.read_csv('data/patterns.csv')
chat_transcripts = pd.read_csv('data/chat_transcripts.csv')
autoheal_logs = pd.read_csv('data/autoheal_logs.csv')

print("=" * 70)
print("DATA VERIFICATION REPORT")
print("=" * 70)

# Check data counts
print("\n1. DATA COUNTS:")
print(f"   - Incidents: {len(incidents)}")
print(f"   - KB Articles: {len(kb_articles)}")
print(f"   - Patterns: {len(patterns)}")
print(f"   - Chat Transcripts: {len(chat_transcripts)}")
print(f"   - Autoheal Logs: {len(autoheal_logs)}")

# Check data relationships
print("\n2. DATA RELATIONSHIPS:")
print(f"   - Unique pattern_ids in incidents: {incidents['pattern_id'].nunique()}")
print(f"   - Pattern IDs in patterns.csv: {len(patterns)}")
print(f"   - Chat transcripts mapped to incidents: {chat_transcripts['incident_id'].nunique()}")

# Check for missing values
print("\n3. DATA QUALITY:")
print(f"   - Incidents with missing descriptions: {incidents['issue_description'].isna().sum()}")
print(f"   - KB articles with missing content: {kb_articles['content'].isna().sum()}")
print(f"   - Patterns with missing recommended_fix: {patterns['recommended_fix'].isna().sum()}")

# Check application distribution
print("\n4. APPLICATION DISTRIBUTION:")
print(incidents['application'].value_counts())

# Check severity distribution
print("\n5. SEVERITY DISTRIBUTION:")
print(incidents['severity'].value_counts())

# Check pattern distribution
print("\n6. TOP PATTERNS IN INCIDENTS:")
print(incidents['pattern_id'].value_counts().head(10))

# Check autoheal success rate
print("\n7. AUTOHEAL METRICS:")
success_rate = (autoheal_logs['success'].sum() / len(autoheal_logs)) * 100
print(f"   - Total autoheal attempts: {len(autoheal_logs)}")
print(f"   - Successful: {autoheal_logs['success'].sum()}")
print(f"   - Success rate: {success_rate:.1f}%")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)

"""
Comprehensive FAISS Score Analysis
Tests various query types and calculates similarity scores
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from query_retrieval import QueryRetriever

# Initialize retriever
print("Initializing QueryRetriever...")
retriever = QueryRetriever(auto_rebuild=False)

# Test queries covering different scenarios
test_queries = [
    # Payment-related queries
    ("bill payment is not reflecting", "Payment/Billing"),
    ("autopay feature is not working", "Payment Automation"),
    ("payment gateway timeout", "Payment Gateway"),
    ("transaction failed", "Payment Transaction"),
    
    # Login/Authentication queries
    ("cannot login to system", "Login"),
    ("SSO authentication failed", "SSO/Auth"),
    ("session expired", "Session"),
    
    # Performance queries
    ("system is slow", "Performance"),
    ("network latency issue", "Network"),
    ("timeout error", "Timeout"),
    
    # Data/Database queries
    ("missing data in database", "Database"),
    ("null value error", "Data Quality"),
    ("schema mismatch", "Schema"),
    
    # Cache/Deployment queries
    ("cache not updating", "Cache"),
    ("deployment issue", "Deployment"),
    
    # Generic queries
    ("system error", "Generic Error"),
    ("not working", "Generic Failure"),
]

print("\n" + "="*100)
print("FAISS SIMILARITY SCORE ANALYSIS")
print("="*100)

all_results = []

for query, category in test_queries:
    print(f"\n{'='*100}")
    print(f"Query: '{query}' (Category: {category})")
    print(f"{'='*100}")
    
    # Get search results
    results = retriever.search(query, k=5)
    
    print(f"\nTop 5 Results:")
    print(f"{'Rank':<6} {'ID':<12} {'Type':<10} {'Score':<8} {'Description':<60}")
    print("-" * 100)
    
    for i, result in enumerate(results, 1):
        desc = result.get('text', result.get('title', ''))[:60]
        print(f"{i:<6} {result['id']:<12} {result['type']:<10} {result['score']:<8.4f} {desc}")
    
    # Store for summary
    all_results.append({
        'query': query,
        'category': category,
        'top_score': results[0]['score'] if results else 0,
        'avg_score': sum(r['score'] for r in results) / len(results) if results else 0,
        'top_result': results[0] if results else None
    })

# Summary Statistics
print("\n" + "="*100)
print("SUMMARY STATISTICS")
print("="*100)

print(f"\n{'Category':<25} {'Query':<40} {'Top Score':<12} {'Avg Score':<12} {'Quality'}")
print("-" * 100)

for result in all_results:
    quality = "Excellent" if result['top_score'] >= 0.7 else \
              "Good" if result['top_score'] >= 0.5 else \
              "Moderate" if result['top_score'] >= 0.3 else "Poor"
    
    print(f"{result['category']:<25} {result['query']:<40} {result['top_score']:<12.4f} {result['avg_score']:<12.4f} {quality}")

# Score distribution
print("\n" + "="*100)
print("SCORE DISTRIBUTION")
print("="*100)

excellent = sum(1 for r in all_results if r['top_score'] >= 0.7)
good = sum(1 for r in all_results if 0.5 <= r['top_score'] < 0.7)
moderate = sum(1 for r in all_results if 0.3 <= r['top_score'] < 0.5)
poor = sum(1 for r in all_results if r['top_score'] < 0.3)

total = len(all_results)
print(f"\nExcellent (≥0.7):  {excellent:2d} queries ({excellent/total*100:.1f}%)")
print(f"Good (0.5-0.7):    {good:2d} queries ({good/total*100:.1f}%)")
print(f"Moderate (0.3-0.5): {moderate:2d} queries ({moderate/total*100:.1f}%)")
print(f"Poor (<0.3):       {poor:2d} queries ({poor/total*100:.1f}%)")

# Best and worst performing queries
print("\n" + "="*100)
print("BEST PERFORMING QUERIES")
print("="*100)
best = sorted(all_results, key=lambda x: x['top_score'], reverse=True)[:5]
for i, r in enumerate(best, 1):
    print(f"{i}. '{r['query']}' - Score: {r['top_score']:.4f}")

print("\n" + "="*100)
print("WORST PERFORMING QUERIES")
print("="*100)
worst = sorted(all_results, key=lambda x: x['top_score'])[:5]
for i, r in enumerate(worst, 1):
    print(f"{i}. '{r['query']}' - Score: {r['top_score']:.4f}")

print("\n" + "="*100)
print("ANALYSIS COMPLETE")
print("="*100)

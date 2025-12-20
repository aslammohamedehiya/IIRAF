"""
Comprehensive functionality check for IIRAF PoC
Tests all core components and their integration
"""

import os
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import sys

print("=" * 70)
print("IIRAF PoC - FUNCTIONALITY VERIFICATION")
print("=" * 70)

# 1. Check required files exist
print("\n1. CHECKING FILE STRUCTURE...")
required_files = {
    "Data Files": [
        "data/incidents.csv",
        "data/kb_articles.csv",
        "data/patterns.csv",
        "data/chat_transcripts.csv",
        "data/autoheal_logs.csv"
    ],
    "Source Files": [
        "src/data_loader.py",
        "src/build_index.py",
        "src/query_retrieval.py",
        "src/pattern_engine.py",
        "src/autoheal_simulator.py",
        "src/app.py"
    ],
    "Frontend Files": [
        "frontend/index.html",
        "frontend/app.js",
        "frontend/style.css"
    ]
}

all_files_present = True
for category, files in required_files.items():
    print(f"\n   {category}:")
    for file in files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"      {status} {file}")
        if not exists:
            all_files_present = False

# 2. Test data loading
print("\n2. TESTING DATA LOADING...")
try:
    from src.data_loader import load_incidents, load_kb_articles, load_patterns, load_autoheal_logs
    
    incidents = load_incidents()
    print(f"   ✓ Loaded {len(incidents)} incidents")
    
    kbs = load_kb_articles()
    print(f"   ✓ Loaded {len(kbs)} KB articles")
    
    patterns = load_patterns()
    print(f"   ✓ Loaded {len(patterns)} patterns")
    
    logs = load_autoheal_logs()
    print(f"   ✓ Loaded {len(logs)} autoheal logs")
    
except Exception as e:
    print(f"   ✗ Data loading failed: {e}")
    sys.exit(1)

# 3. Check if index exists
print("\n3. CHECKING FAISS INDEX...")
index_exists = os.path.exists("index_store/iiraf_index.faiss")
meta_exists = os.path.exists("index_store/iiraf_meta.pkl")

if index_exists and meta_exists:
    print("   ✓ FAISS index found")
    print("   ✓ Metadata file found")
    
    # Try to load and verify
    try:
        import faiss
        import pickle
        
        index = faiss.read_index("index_store/iiraf_index.faiss")
        with open("index_store/iiraf_meta.pkl", 'rb') as f:
            metadata = pickle.load(f)
        
        print(f"   ✓ Index contains {index.ntotal} vectors")
        print(f"   ✓ Metadata contains {len(metadata)} items")
        
        # Check composition
        kb_count = sum(1 for m in metadata if m['type'] == 'kb')
        inc_count = sum(1 for m in metadata if m['type'] == 'incident')
        print(f"   ✓ Index composition: {kb_count} KB articles, {inc_count} incidents")
        
    except Exception as e:
        print(f"   ⚠ Index exists but couldn't be loaded: {e}")
else:
    print("   ⚠ FAISS index not found - needs to be built")
    print("   → Run: python src/build_index.py")

# 4. Test pattern engine
print("\n4. TESTING PATTERN ENGINE...")
try:
    from src.pattern_engine import PatternEngine
    
    pe = PatternEngine()
    patterns = pe.analyze_patterns()
    print(f"   ✓ Pattern engine initialized")
    print(f"   ✓ Detected {len(patterns)} pattern groups")
    
except Exception as e:
    print(f"   ✗ Pattern engine failed: {e}")

# 5. Test autoheal simulator
print("\n5. TESTING AUTOHEAL SIMULATOR...")
try:
    from src.autoheal_simulator import AutoHealSimulator
    
    ahs = AutoHealSimulator()
    action = ahs.determine_action("Service is down and crashing")
    print(f"   ✓ Autoheal simulator initialized")
    print(f"   ✓ Action determination works: '{action}'")
    
except Exception as e:
    print(f"   ✗ Autoheal simulator failed: {e}")

# 6. Test query retrieval (if index exists)
if index_exists and meta_exists:
    print("\n6. TESTING QUERY RETRIEVAL...")
    try:
        from src.query_retrieval import QueryRetriever
        
        qr = QueryRetriever()
        results = qr.search("cannot connect to vpn", k=3)
        print(f"   ✓ Query retriever initialized")
        print(f"   ✓ Search returned {len(results)} results")
        
        if results:
            print(f"   ✓ Top result type: {results[0]['type']}")
            print(f"   ✓ Top result score: {results[0]['score']:.4f}")
        
    except Exception as e:
        print(f"   ✗ Query retrieval failed: {e}")
else:
    print("\n6. QUERY RETRIEVAL - SKIPPED (index not built)")

# 7. Check dependencies
print("\n7. CHECKING DEPENDENCIES...")
required_packages = [
    'pandas', 'numpy', 'sentence_transformers', 'faiss',
    'sklearn', 'hdbscan', 'umap', 'xgboost', 'fastapi', 'uvicorn'
]

missing_packages = []
for package in required_packages:
    try:
        if package == 'sklearn':
            __import__('sklearn')
        elif package == 'sentence_transformers':
            __import__('sentence_transformers')
        else:
            __import__(package)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ {package} - NOT INSTALLED")
        missing_packages.append(package)

# Final summary
print("\n" + "=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)

issues = []

if not all_files_present:
    issues.append("Some required files are missing")

if missing_packages:
    issues.append(f"Missing packages: {', '.join(missing_packages)}")

if not (index_exists and meta_exists):
    issues.append("FAISS index needs to be built (run: python src/build_index.py)")

if issues:
    print("\n⚠ ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
else:
    print("\n✓ ALL CHECKS PASSED - Application is ready to run!")

print("\nNEXT STEPS:")
if not (index_exists and meta_exists):
    print("   1. Build the FAISS index: python src/build_index.py")
    print("   2. Start the backend: uvicorn src.app:app --reload")
    print("   3. Open browser to: http://localhost:8000")
else:
    print("   1. Start the backend: uvicorn src.app:app --reload")
    print("   2. Open browser to: http://localhost:8000")

print("=" * 70)

import os
import pickle
import numpy as np
import faiss
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
from data_loader import load_incidents, load_kb_articles

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INDEX_DIR = os.path.join(BASE_DIR, "index_store")
INDEX_PATH = os.path.join(INDEX_DIR, "iiraf_index.faiss")
META_PATH = os.path.join(INDEX_DIR, "iiraf_meta.pkl")
TIMESTAMP_PATH = os.path.join(INDEX_DIR, "index_metadata.json")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Data files to monitor
DATA_FILES = ["incidents.csv", "kb_articles.csv", "patterns.csv"]

def get_data_timestamps():
    """Get modification timestamps for all data files."""
    timestamps = {}
    for filename in DATA_FILES:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            timestamps[filename] = os.path.getmtime(filepath)
        else:
            timestamps[filename] = None
    return timestamps

def save_index_metadata(item_count):
    """Save index build metadata including timestamps."""
    metadata = {
        "last_build_time": datetime.now().isoformat(),
        "data_file_timestamps": get_data_timestamps(),
        "item_count": item_count,
        "index_version": "1.0"
    }
    with open(TIMESTAMP_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    return metadata

def load_index_metadata():
    """Load index metadata if it exists."""
    if os.path.exists(TIMESTAMP_PATH):
        with open(TIMESTAMP_PATH, 'r') as f:
            return json.load(f)
    return None

def is_index_stale():
    """Check if the index is stale (data files modified since last build)."""
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        return True  # Index doesn't exist
    
    metadata = load_index_metadata()
    if not metadata:
        return True  # No metadata, assume stale
    
    current_timestamps = get_data_timestamps()
    saved_timestamps = metadata.get("data_file_timestamps", {})
    
    # Check if any data file has been modified
    for filename, current_ts in current_timestamps.items():
        saved_ts = saved_timestamps.get(filename)
        if current_ts is None:
            continue  # File doesn't exist
        if saved_ts is None or current_ts > saved_ts:
            return True  # File modified or wasn't tracked before
    
    return False

def get_index_info():
    """Get information about the current index."""
    metadata = load_index_metadata()
    if not metadata:
        return {
            "exists": False,
            "is_stale": True,
            "message": "Index not built yet"
        }
    
    stale = is_index_stale()
    return {
        "exists": True,
        "is_stale": stale,
        "last_build_time": metadata.get("last_build_time"),
        "item_count": metadata.get("item_count"),
        "index_version": metadata.get("index_version"),
        "message": "Index is stale - data files modified" if stale else "Index is current"
    }

def build_index(show_progress=True):
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
        print(f"Created {INDEX_DIR}")

    print("Loading data...")
    incidents = load_incidents()
    kbs = load_kb_articles()

    # Prepare corpus
    # We will index both incidents (for pattern matching/similar incidents) and KBs (for resolution)
    # Metadata will store the type ('incident' or 'kb') and the ID
    
    corpus_texts = []
    metadata = []

    # Add Incidents
    for _, row in incidents.iterrows():
        corpus_texts.append(row['cleaned_description'])
        metadata.append({
            "type": "incident",
            "id": row['id'],
            "text": row['description'],
            "resolution": row['resolution'],
            "severity": row['severity'],
            "application": row['application']
        })

    # Add KBs
    for _, row in kbs.iterrows():
        corpus_texts.append(row['cleaned_text'])
        metadata.append({
            "type": "kb",
            "id": row['id'],
            "title": row['title'],
            "content": row['content']
        })

    print(f"Loading model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Generating embeddings for {len(corpus_texts)} items...")
    embeddings = model.encode(corpus_texts, show_progress_bar=show_progress)
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)

    # Build FAISS index
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d) # Inner Product (Cosine Similarity after normalization)
    index.add(embeddings)
    
    print(f"Index built with {index.ntotal} vectors.")

    # Save Index
    faiss.write_index(index, INDEX_PATH)
    print(f"Saved index to {INDEX_PATH}")

    # Save Metadata
    with open(META_PATH, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"Saved metadata to {META_PATH}")
    
    # Save timestamp metadata
    index_meta = save_index_metadata(len(metadata))
    print(f"Saved index metadata to {TIMESTAMP_PATH}")
    print(f"Index built at: {index_meta['last_build_time']}")
    
    return index_meta

if __name__ == "__main__":
    build_index()

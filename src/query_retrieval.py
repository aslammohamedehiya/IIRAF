
"""Query FAISS index for similar incidents and KBs"""
import faiss
import pickle
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from build_index import build_index, is_index_stale, get_index_info

# Paths
INDEX_PATH = r"C:\Aslam BITS\IIRAF requirement\IIRAF_PoC_Starter\index_store\iiraf_index.faiss"
META_PATH = r"C:\Aslam BITS\IIRAF requirement\IIRAF_PoC_Starter\index_store\iiraf_meta.pkl"

class QueryRetriever:
    def __init__(self, auto_rebuild=True):
        """Initialize QueryRetriever with optional auto-rebuild on stale index.
        
        Args:
            auto_rebuild: If True, automatically rebuild index if stale on startup
        """
        # Check if index is stale before loading
        if auto_rebuild and is_index_stale():
            print("WARNING: FAISS index is stale! Data files modified since last build.")
            print("Auto-rebuilding index...")
            try:
                build_index()
                print("SUCCESS: Index rebuilt successfully!")
            except Exception as e:
                print(f"ERROR: Error rebuilding index: {e}")
                print("WARNING: Proceeding with existing index (may be stale)")
        
        print("Loading FAISS index and metadata...")
        self.index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, 'rb') as f:
            self.metadata = pickle.load(f)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Display index info
        info = get_index_info()
        print(f"QueryRetriever initialized with {info.get('item_count', 'unknown')} items.")
        if info.get('is_stale'):
            print("WARNING: Index may still be stale!")

    def search(self, query: str, k: int = 10, threshold: float = 12.0) -> List[Dict]:
        """
        Search for similar incidents/KBs with similarity threshold.
        
        Args:
            query: Search query text
            k: Number of results to retrieve from FAISS
            threshold: Maximum L2 distance (lower = more similar). Results with
                      distance > threshold are filtered out. Default 12.0.
        
        Returns:
            List of relevant items with similarity scores
        """
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        filtered_count = 0
        
        for i, idx in enumerate(indices[0]):
            if idx == -1: 
                continue
            
            # Filter by similarity threshold
            distance = float(distances[0][i])
            if distance > threshold:
                filtered_count += 1
                continue  # Skip irrelevant results
            
            item = self.metadata[idx]
            
            # Convert L2 distance to similarity score (0-1, higher is better)
            # Using inverse: score = 1 / (1 + distance)
            similarity_score = 1.0 / (1.0 + distance)
            
            results.append({
                "id": str(item.get("id", "N/A")),
                "type": item.get("type", "unknown"),
                "text": item.get("text", ""),
                "resolution": item.get("resolution", ""),  # For incidents
                "content": item.get("content", ""),        # For KBs
                "title": item.get("title", ""),            # For KBs
                "score": similarity_score,  # Now using normalized score
                "distance": distance  # Keep raw distance for debugging
            })
        
        if filtered_count > 0:
            print(f"Filtered out {filtered_count} irrelevant results (distance > {threshold})")
        
        return results

    def get_mapped_kb_articles(self, incident_ids: List[str]) -> List[Dict]:
        """
        Get KB articles that map to the given incidents based on application and root_cause.
        """
        import pandas as pd
        import os
        
        # Load incidents and KB articles
        base_dir = os.path.dirname(os.path.dirname(__file__))
        incidents_path = os.path.join(base_dir, "data", "incidents.csv")
        kb_path = os.path.join(base_dir, "data", "kb_articles.csv")
        
        incidents_df = pd.read_csv(incidents_path)
        kb_df = pd.read_csv(kb_path)
        
        # Filter incidents by the given IDs
        filtered_incidents = incidents_df[incidents_df['incident_id'].isin(incident_ids)]
        
        if filtered_incidents.empty:
            return []
        
        # Get unique combinations of application and root_cause
        app_root_pairs = set()
        for _, inc in filtered_incidents.iterrows():
            app_root_pairs.add((inc['application'], inc['root_cause']))
        
        # Find matching KB articles
        matched_kbs = []
        for _, kb in kb_df.iterrows():
            # Check if KB matches any incident's application and root cause
            for app, root_cause in app_root_pairs:
                if kb['application'] == app and root_cause.lower() in kb['title'].lower():
                    matched_kbs.append({
                        "id": kb['kb_id'],
                        "type": "kb",
                        "title": kb['title'],
                        "content": kb['content'],
                        "application": kb['application'],
                        "text": kb['title'] + " " + kb['content'],
                        "score": 1.0  # Perfect match since it's mapped
                    })
                    break  # Avoid duplicates
        
        return matched_kbs
    
    def reload_index(self):
        """Reload the FAISS index and metadata without restarting the server.
        
        Returns:
            dict: Status information about the reload operation
        """
        try:
            print("Reloading FAISS index...")
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, 'rb') as f:
                self.metadata = pickle.load(f)
            
            info = get_index_info()
            print(f"SUCCESS: Index reloaded successfully with {info.get('item_count', 'unknown')} items.")
            return {
                "success": True,
                "message": "Index reloaded successfully",
                "info": info
            }
        except Exception as e:
            print(f"ERROR: Error reloading index: {e}")
            return {
                "success": False,
                "message": f"Error reloading index: {str(e)}"
            }
    
    def validate_index(self):
        """Check if the current index is stale.
        
        Returns:
            dict: Index validation information
        """
        info = get_index_info()
        return {
            "is_stale": info.get('is_stale', True),
            "last_build_time": info.get('last_build_time'),
            "item_count": info.get('item_count'),
            "message": info.get('message')
        }

if __name__ == "__main__":
    qr = QueryRetriever()
    print(qr.search("cannot connect to vpn"))

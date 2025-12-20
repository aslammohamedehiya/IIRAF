from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from src.query_retrieval import QueryRetriever
from src.pattern_engine import PatternEngine
from src.autoheal_simulator import AutoHealSimulator
from src.build_index import build_index, get_index_info
from src.solution_generator import SolutionGenerator
import time

app = FastAPI(title="IIRAF PoC API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
try:
    retriever = QueryRetriever()
    pattern_engine = PatternEngine()
    healer = AutoHealSimulator()
    solution_generator = SolutionGenerator()
except Exception as e:
    print(f"Error initializing modules: {e}")

# Models
class SearchQuery(BaseModel):
    query: str

class HealRequest(BaseModel):
    action: str
    target: str

class SolutionRequest(BaseModel):
    query: str
    results: List[dict]

# Endpoints
@app.get("/health")
def health():
    """Health check endpoint with index status."""
    index_info = get_index_info()
    return {
        "status": "ok",
        "index_status": {
            "exists": index_info.get("exists", False),
            "is_stale": index_info.get("is_stale", True),
            "item_count": index_info.get("item_count", 0)
        }
    }

@app.post("/api/search")
def search_incidents(payload: SearchQuery):
    # Get all search results
    all_results = retriever.search(payload.query)
    
    # Separate incidents and KB articles from search results
    incidents = [r for r in all_results if r['type'] == 'incident']
    
    # Get incident IDs
    incident_ids = [inc['id'] for inc in incidents]
    
    # Get mapped KB articles based on the incidents
    mapped_kbs = retriever.get_mapped_kb_articles(incident_ids)
    
    # Combine results with incidents first, then mapped KBs
    results = incidents + mapped_kbs
    
    return {"results": results}

@app.get("/api/patterns")
def get_patterns():
    patterns = pattern_engine.analyze_patterns()
    return {"patterns": patterns}

@app.post("/api/heal")
def trigger_heal(payload: HealRequest):
    result = healer.execute_heal(payload.action, payload.target)
    return result

@app.post("/api/generate-solution")
def generate_solution(payload: SolutionRequest):
    """Generate AI-powered solution based on search results."""
    try:
        solution = solution_generator.generate_solution(
            query=payload.query,
            search_results=payload.results
        )
        return solution
    except Exception as e:
        print(f"Error generating solution: {e}")
        # Return fallback solution
        return {
            'steps': ['Unable to generate AI solution. Please review the supporting evidence manually.'],
            'source': 'error',
            'metadata': {'error': str(e)}
        }

@app.get("/api/index/status")
def get_index_status():
    """Get current FAISS index status and metadata."""
    info = get_index_info()
    return info

@app.post("/api/index/refresh")
def refresh_index():
    """Manually trigger FAISS index rebuild."""
    try:
        start_time = time.time()
        print("Manual index refresh triggered...")
        
        # Rebuild the index (disable progress bar for API calls)
        index_meta = build_index(show_progress=False)
        
        # Reload the index in the retriever
        reload_result = retriever.reload_index()
        
        build_time = time.time() - start_time
        
        if reload_result.get("success"):
            return {
                "success": True,
                "message": "Index rebuilt and reloaded successfully",
                "build_time_seconds": round(build_time, 2),
                "item_count": index_meta.get("item_count"),
                "last_build_time": index_meta.get("last_build_time")
            }
        else:
            return {
                "success": False,
                "message": "Index rebuilt but failed to reload",
                "error": reload_result.get("message")
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error refreshing index: {str(e)}"
        }

# Serve Frontend
# Assuming we will put frontend files in 'frontend' folder at root or specific static folder
# Adjusting to serve from the 'frontend' directory relative to where this script might be run or root
import os
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

"""
UMAP-based visualization for incident analysis
Generates 2D/3D coordinates for visualizing incident patterns
"""
import numpy as np
import umap
import pandas as pd
from sentence_transformers import SentenceTransformer
import os

class IncidentVisualizer:
    def __init__(self):
        """Initialize UMAP visualizer"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.reducer_2d = umap.UMAP(
            n_components=2,
            n_neighbors=15,
            min_dist=0.1,
            metric='cosine',
            random_state=42
        )
        self.reducer_3d = umap.UMAP(
            n_components=3,
            n_neighbors=15,
            min_dist=0.1,
            metric='cosine',
            random_state=42
        )
        self.embeddings = None
        self.coords_2d = None
        self.coords_3d = None
        
    def load_incidents(self):
        """Load incident data"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        df = pd.read_csv(os.path.join(data_dir, "incidents.csv"))
        
        # Map field names
        if 'incident_id' in df.columns:
            df['id'] = df['incident_id']
        if 'issue_description' in df.columns:
            df['description'] = df['issue_description']
        if 'issue_summary' in df.columns:
            df['summary'] = df['issue_summary']
            
        return df
    
    def generate_incident_map_2d(self, filter_severity=None, filter_application=None):
        """
        Generate 2D visualization coordinates for incidents
        
        Args:
            filter_severity: Optional severity filter (e.g., 'High', 'Critical')
            filter_application: Optional application filter
            
        Returns:
            Dictionary with coordinates and metadata
        """
        df = self.load_incidents()
        
        # Apply filters
        if filter_severity:
            df = df[df['severity'] == filter_severity]
        if filter_application:
            df = df[df['application'] == filter_application]
        
        if len(df) < 2:
            return {"error": "Not enough data points for visualization"}
        
        # Generate embeddings
        descriptions = df['description'].fillna('').tolist()
        self.embeddings = self.model.encode(descriptions, show_progress_bar=False)
        
        # Reduce to 2D
        self.coords_2d = self.reducer_2d.fit_transform(self.embeddings)
        
        # Prepare response
        severity_colors = {
            'Low': '#4CAF50',      # Green
            'Medium': '#FFC107',   # Amber
            'High': '#FF9800',     # Orange
            'Critical': '#F44336'  # Red
        }
        
        return {
            "coordinates": self.coords_2d.tolist(),
            "metadata": {
                "incident_ids": df['id'].tolist(),
                "descriptions": [desc[:100] + "..." for desc in df['description'].tolist()],
                "summaries": df.get('summary', df['description']).tolist(),
                "severities": df['severity'].tolist(),
                "applications": df['application'].tolist(),
                "colors": [severity_colors.get(sev, '#9E9E9E') for sev in df['severity']],
                "created_at": df.get('created_at', ['N/A'] * len(df)).tolist()
            },
            "filters": {
                "severity": filter_severity,
                "application": filter_application
            },
            "stats": {
                "total_incidents": len(df),
                "severity_distribution": df['severity'].value_counts().to_dict(),
                "application_distribution": df['application'].value_counts().to_dict()
            }
        }
    
    def generate_incident_map_3d(self):
        """Generate 3D visualization coordinates"""
        df = self.load_incidents()
        
        if len(df) < 2:
            return {"error": "Not enough data points for visualization"}
        
        # Generate embeddings
        descriptions = df['description'].fillna('').tolist()
        self.embeddings = self.model.encode(descriptions, show_progress_bar=False)
        
        # Reduce to 3D
        self.coords_3d = self.reducer_3d.fit_transform(self.embeddings)
        
        severity_colors = {
            'Low': '#4CAF50',
            'Medium': '#FFC107',
            'High': '#FF9800',
            'Critical': '#F44336'
        }
        
        return {
            "coordinates": self.coords_3d.tolist(),
            "metadata": {
                "incident_ids": df['id'].tolist(),
                "descriptions": [desc[:100] + "..." for desc in df['description'].tolist()],
                "severities": df['severity'].tolist(),
                "applications": df['application'].tolist(),
                "colors": [severity_colors.get(sev, '#9E9E9E') for sev in df['severity']]
            },
            "stats": {
                "total_incidents": len(df),
                "severity_distribution": df['severity'].value_counts().to_dict()
            }
        }
    
    def get_available_filters(self):
        """Get available filter options"""
        df = self.load_incidents()
        
        return {
            "severities": sorted(df['severity'].unique().tolist()),
            "applications": sorted(df['application'].unique().tolist()),
            "total_incidents": len(df)
        }

if __name__ == "__main__":
    visualizer = IncidentVisualizer()
    
    print("Generating 2D incident map...")
    result_2d = visualizer.generate_incident_map_2d()
    
    if "error" not in result_2d:
        print(f"[OK] Generated 2D coordinates for {result_2d['stats']['total_incidents']} incidents")
        print(f"  Severity distribution: {result_2d['stats']['severity_distribution']}")
        print(f"  Applications: {list(result_2d['stats']['application_distribution'].keys())}")
    else:
        print(f"[ERROR] {result_2d['error']}")
    
    print("\nAvailable filters:")
    filters = visualizer.get_available_filters()
    print(f"  Severities: {filters['severities']}")
    print(f"  Applications: {filters['applications']}")


"""Detect recurring incident patterns using HDBSCAN clustering"""
import pandas as pd
import numpy as np
import hdbscan
from sentence_transformers import SentenceTransformer
from collections import Counter
import os

class PatternEngine:
    def __init__(self):
        # Load incidents data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        try:
            self.df = pd.read_csv(os.path.join(data_dir, "incidents.csv"))
            # Map field names
            if 'incident_id' in self.df.columns:
                self.df['id'] = self.df['incident_id']
            if 'issue_description' in self.df.columns:
                self.df['description'] = self.df['issue_description']
        except Exception as e:
            print(f"Error loading incidents: {e}")
            self.df = pd.DataFrame(columns=["description", "severity", "application"])
        
        # Initialize models
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.clusterer = None
        self.embeddings = None
        self.cluster_labels = None

    def analyze_patterns(self):
        """
        Detect patterns using HDBSCAN clustering.
        Returns both cluster-based patterns and frequency-based fallback.
        """
        if self.df.empty or len(self.df) < 5:
            return self._fallback_patterns()
        
        try:
            # Use HDBSCAN clustering
            return self.detect_clusters()
        except Exception as e:
            print(f"Clustering failed: {e}, falling back to frequency analysis")
            return self._fallback_patterns()

    def detect_clusters(self):
        """Use HDBSCAN to find incident clusters"""
        print(f"Clustering {len(self.df)} incidents...")
        
        # Generate embeddings
        descriptions = self.df['description'].fillna('').tolist()
        self.embeddings = self.model.encode(descriptions, show_progress_bar=False)
        
        # Cluster with HDBSCAN
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=5,
            min_samples=3,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        self.cluster_labels = self.clusterer.fit_predict(self.embeddings)
        
        # Analyze clusters
        patterns = []
        unique_clusters = set(self.cluster_labels)
        
        # Process each cluster (skip noise cluster -1)
        for cluster_id in sorted(unique_clusters):
            if cluster_id == -1:  # Noise/outliers
                continue
                
            cluster_mask = self.cluster_labels == cluster_id
            cluster_incidents = self.df[cluster_mask]
            
            if len(cluster_incidents) == 0:
                continue
            
            # Get cluster characteristics
            pattern = {
                "pattern_id": f"CLUSTER-{cluster_id}",
                "description": self._get_cluster_description(cluster_incidents),
                "frequency": len(cluster_incidents),
                "severity": self._calculate_cluster_severity(cluster_incidents),
                "applications": cluster_incidents['application'].value_counts().head(3).to_dict(),
                "incidents": cluster_incidents['id'].tolist()[:5],  # Sample incidents
                "representative": self._get_representative(cluster_incidents, cluster_mask),
                "recommended_action": self._get_recommended_action(cluster_incidents)
            }
            patterns.append(pattern)
        
        # Add anomaly detection
        anomalies = self._detect_anomalies()
        if anomalies:
            patterns.append(anomalies)
        
        # Sort by frequency
        patterns.sort(key=lambda x: x['frequency'], reverse=True)
        
        print(f"Found {len(patterns)} patterns (including {len([p for p in patterns if 'CLUSTER' in p['pattern_id']])} clusters)")
        return patterns

    def _get_cluster_description(self, cluster_incidents):
        """Generate a description for the cluster"""
        # Get most common application
        top_app = cluster_incidents['application'].mode()
        app_name = top_app.iloc[0] if len(top_app) > 0 else "Unknown"
        
        # Get most common keywords from descriptions
        all_text = ' '.join(cluster_incidents['description'].fillna('').tolist()).lower()
        words = all_text.split()
        # Filter common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are'}
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        common_keywords = Counter(keywords).most_common(3)
        
        if common_keywords:
            keyword_str = ', '.join([k[0] for k in common_keywords])
            return f"Recurring {app_name} issues related to: {keyword_str}"
        else:
            return f"Recurring {app_name} incidents"

    def _calculate_cluster_severity(self, cluster_incidents):
        """Calculate overall severity for cluster"""
        severity_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        severities = cluster_incidents['severity'].map(severity_map).fillna(1)
        avg_severity = severities.mean()
        
        if avg_severity >= 3.5:
            return "Critical"
        elif avg_severity >= 2.5:
            return "High"
        elif avg_severity >= 1.5:
            return "Medium"
        else:
            return "Low"

    def _get_representative(self, cluster_incidents, cluster_mask):
        """Get the most representative incident from cluster"""
        # Find incident closest to cluster centroid
        cluster_embeddings = self.embeddings[cluster_mask]
        centroid = np.mean(cluster_embeddings, axis=0)
        
        # Calculate distances to centroid
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
        closest_idx = np.argmin(distances)
        
        representative = cluster_incidents.iloc[closest_idx]
        return {
            "id": representative['id'],
            "description": representative['description'][:100] + "...",
            "resolution": representative.get('resolution', 'N/A')[:100] + "..."
        }

    def _get_recommended_action(self, cluster_incidents):
        """Recommend action based on cluster characteristics"""
        avg_severity = cluster_incidents['severity'].value_counts().idxmax()
        app = cluster_incidents['application'].mode().iloc[0] if len(cluster_incidents) > 0 else "Unknown"
        
        if len(cluster_incidents) > 20:
            return f"High-priority: Investigate root cause for {app} - {len(cluster_incidents)} similar incidents"
        elif avg_severity in ['Critical', 'High']:
            return f"Auto-heal recommended for {app} incidents"
        else:
            return f"Monitor {app} for pattern escalation"

    def _detect_anomalies(self):
        """Detect anomalous incidents (outliers)"""
        if self.cluster_labels is None:
            return None
        
        anomaly_mask = self.cluster_labels == -1
        anomalies = self.df[anomaly_mask]
        
        if len(anomalies) == 0:
            return None
        
        return {
            "pattern_id": "ANOMALIES",
            "description": "Unusual incidents that don't fit known patterns",
            "frequency": len(anomalies),
            "severity": "Medium",
            "applications": anomalies['application'].value_counts().head(3).to_dict(),
            "incidents": anomalies['id'].tolist()[:5],
            "representative": {
                "id": "Multiple",
                "description": "Various unique incidents",
                "resolution": "Requires individual investigation"
            },
            "recommended_action": "Review anomalies for new emerging patterns"
        }

    def _fallback_patterns(self):
        """Fallback to simple frequency analysis if clustering fails"""
        if self.df.empty:
            return []
        
        # Simple frequency analysis by application
        top_applications = self.df['application'].value_counts().head(5).to_dict()
        
        patterns = []
        for app, count in top_applications.items():
            patterns.append({
                "pattern_id": f"PAT-{abs(hash(app)) % 1000}",
                "description": f"Frequent {app} issues detected",
                "frequency": int(count),
                "severity": "High" if count > 20 else "Medium",
                "applications": {app: count},
                "incidents": [],
                "representative": {"id": "N/A", "description": "N/A", "resolution": "N/A"},
                "recommended_action": f"Auto-heal enabled for {app}"
            })
            
        return patterns

    def get_cluster_details(self, cluster_id):
        """Get detailed information about a specific cluster"""
        if self.cluster_labels is None:
            return None
        
        # Extract cluster number from pattern_id
        try:
            cluster_num = int(cluster_id.split('-')[1])
        except:
            return None
        
        cluster_mask = self.cluster_labels == cluster_num
        cluster_incidents = self.df[cluster_mask]
        
        return {
            "cluster_id": cluster_id,
            "size": len(cluster_incidents),
            "incidents": cluster_incidents.to_dict('records'),
            "severity_distribution": cluster_incidents['severity'].value_counts().to_dict(),
            "application_distribution": cluster_incidents['application'].value_counts().to_dict()
        }

if __name__ == "__main__":
    pe = PatternEngine()
    patterns = pe.analyze_patterns()
    
    print("\n=== Detected Patterns ===")
    for pattern in patterns:
        print(f"\n{pattern['pattern_id']}: {pattern['description']}")
        print(f"  Frequency: {pattern['frequency']}")
        print(f"  Severity: {pattern['severity']}")
        print(f"  Action: {pattern['recommended_action']}")

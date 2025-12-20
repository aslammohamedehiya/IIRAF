
"""Detect recurring incident patterns using clustering"""
import pandas as pd
from collections import Counter

class PatternEngine:
    def __init__(self):
        # In a real system, this would load live incidents from DB
        try:
            self.df = pd.read_csv("data/incidents.csv")
        except:
            self.df = pd.DataFrame(columns=["description", "category", "severity"])

    def analyze_patterns(self):
        """
        Group incidents by application and return high-frequency issues.
        """
        if self.df.empty:
            return []

        # Simple frequency analysis by application (instead of category)
        top_applications = self.df['application'].value_counts().head(5).to_dict()
        
        # Keyword extraction (mock)
        patterns = []
        for app, count in top_applications.items():
            patterns.append({
                "pattern_id": f"PAT-{abs(hash(app)) % 1000}",
                "description": f"Frequent {app} issues detected",
                "frequency": int(count),
                "severity": "High" if count > 10 else "Medium",
                "recommended_action": f"Auto-heal enabled for {app}"
            })
            
        return patterns

if __name__ == "__main__":
    pe = PatternEngine()
    print(pe.analyze_patterns())

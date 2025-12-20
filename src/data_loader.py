import pandas as pd
import os
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def clean_text(text):
    """Basic text cleaning: lowercase, strip whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_incidents():
    """Load incidents.csv"""
    path = os.path.join(DATA_DIR, "incidents.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found.")
    df = pd.read_csv(path)
    # Map new field names to expected names
    df['id'] = df['incident_id']
    df['description'] = df['issue_description']
    # Preprocess description
    df['cleaned_description'] = df['description'].apply(clean_text)
    return df

def load_kb_articles():
    """Load kb_articles.csv"""
    path = os.path.join(DATA_DIR, "kb_articles.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found.")
    df = pd.read_csv(path)
    # Map new field names to expected names
    df['id'] = df['kb_id']
    # Combine title and content for embedding
    df['full_text'] = df['title'] + " " + df['content']
    df['cleaned_text'] = df['full_text'].apply(clean_text)
    return df

def load_patterns():
    """Load patterns.csv"""
    path = os.path.join(DATA_DIR, "patterns.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found.")
    return pd.read_csv(path)

def load_autoheal_logs():
    """Load autoheal_logs.csv"""
    path = os.path.join(DATA_DIR, "autoheal_logs.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found.")
    return pd.read_csv(path)

if __name__ == "__main__":
    # Test loading
    try:
        incidents = load_incidents()
        print(f"Loaded {len(incidents)} incidents.")
        print(incidents.head(2))
        
        kbs = load_kb_articles()
        print(f"Loaded {len(kbs)} KB articles.")
        print(kbs.head(2))
        
    except Exception as e:
        print(f"Error loading data: {e}")

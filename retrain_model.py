"""
Quick script to retrain severity predictor and generate metadata
"""
from src.severity_predictor import SeverityPredictor
import pandas as pd

print("Loading incidents data...")
df = pd.read_csv('data/incidents.csv')

# Map column names to match expected format
if 'issue_description' in df.columns:
    df['description'] = df['issue_description']

print(f"Loaded {len(df)} incidents")
print("\nTraining XGBoost model...")

sp = SeverityPredictor()
results = sp.train(df, retrain=True)  # Force retrain

print("\n" + "="*60)
print("[OK] MODEL TRAINING COMPLETE")
print("="*60)
print(f"Accuracy: {results['accuracy']:.2%}")
print(f"F1 Score: {results['f1_score']:.4f}")
print(f"Training Samples: {results['training_samples']}")
print("\nModel metadata saved to models/model_metadata.json")
print("\nNow restart your backend server and refresh the frontend!")
print("The Model Info link should now show correct accuracy and date.")

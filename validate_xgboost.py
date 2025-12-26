"""
Validate XGBoost Severity Predictor Model
Tests model accuracy, precision, recall, and F1 score on current dataset
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from severity_predictor import SeverityPredictor
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
import numpy as np

print("=" * 80)
print("XGBOOST SEVERITY PREDICTOR - VALIDATION")
print("=" * 80)

# Load the trained model
print("\n[1/5] Loading trained XGBoost model...")
predictor = SeverityPredictor()

if not predictor.is_trained:
    print("[ERROR] Model not trained. Training now...")
    predictor.train(retrain=True)

model_info = predictor.get_model_info()
print(f"[OK] Model loaded: {model_info['model_type']}")
print(f"[OK] Classes: {model_info['classes']}")
print(f"[OK] Features: {model_info['num_features']}")

# Load test data
print("\n[2/5] Loading incident data for validation...")
data_dir = os.path.join(os.path.dirname(__file__), "data")
df = pd.read_csv(os.path.join(data_dir, "incidents.csv"))
print(f"[OK] Loaded {len(df)} incidents")

# Prepare data
X_text = df['issue_description'].fillna('').tolist()
y_true_labels = df['severity'].tolist()

# Map labels to codes
label_encoder = {'Low': 0, 'Medium': 1, 'High': 2, 'Critical': 3}
y_true = [label_encoder[label] for label in y_true_labels]

# Make predictions
print("\n[3/5] Running predictions on all incidents...")
predictions = predictor.predict_batch(X_text)
y_pred_labels = [p['severity'] for p in predictions]
y_pred = [label_encoder[label] for label in y_pred_labels]

# Calculate metrics
print("\n[4/5] Calculating performance metrics...")
accuracy = accuracy_score(y_true, y_pred)
precision, recall, f1, support = precision_recall_fscore_support(
    y_true, y_pred, average='weighted', zero_division=0
)

print(f"\n{'='*80}")
print("OVERALL PERFORMANCE METRICS")
print(f"{'='*80}")
print(f"Accuracy:  {accuracy:.2%}")
print(f"Precision: {precision:.2%}")
print(f"Recall:    {recall:.2%}")
print(f"F1 Score:  {f1:.4f}")

# Per-class metrics
print(f"\n{'='*80}")
print("PER-CLASS PERFORMANCE")
print(f"{'='*80}")

class_names = ['Low', 'Medium', 'High', 'Critical']
precision_per_class, recall_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
    y_true, y_pred, labels=[0, 1, 2, 3], zero_division=0
)

print(f"\n{'Class':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
print("-" * 60)
for i, class_name in enumerate(class_names):
    print(f"{class_name:<12} {precision_per_class[i]:<12.2%} {recall_per_class[i]:<12.2%} "
          f"{f1_per_class[i]:<12.4f} {support_per_class[i]:<10}")

# Confusion Matrix
print(f"\n{'='*80}")
print("CONFUSION MATRIX")
print(f"{'='*80}")
cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3])
header = "Actual \\ Predicted"
print(f"\n{header:<20} {'Low':<10} {'Medium':<10} {'High':<10} {'Critical':<10}")
print("-" * 70)
for i, class_name in enumerate(class_names):
    row = f"{class_name:<20}"
    for j in range(len(class_names)):
        row += f"{cm[i][j]:<10}"
    print(row)

# Calculate accuracy per class
print(f"\n{'='*80}")
print("ACCURACY PER CLASS")
print(f"{'='*80}")
for i, class_name in enumerate(class_names):
    class_total = support_per_class[i]
    class_correct = cm[i][i]
    class_accuracy = class_correct / class_total if class_total > 0 else 0
    print(f"{class_name:<12}: {class_accuracy:.2%} ({class_correct}/{class_total} correct)")

# Sample predictions
print(f"\n{'='*80}")
print("SAMPLE PREDICTIONS (First 10 incidents)")
print(f"{'='*80}")
print(f"\n{'ID':<12} {'Actual':<12} {'Predicted':<12} {'Confidence':<12} {'Match':<8}")
print("-" * 60)
for i in range(min(10, len(df))):
    incident_id = df.iloc[i]['incident_id']
    actual = y_true_labels[i]
    predicted = predictions[i]['severity']
    confidence = predictions[i]['confidence']
    match = "[OK]" if actual == predicted else "[X]"
    print(f"{incident_id:<12} {actual:<12} {predicted:<12} {confidence:<12.2%} {match:<8}")

# Error analysis - show misclassifications
print(f"\n{'='*80}")
print("MISCLASSIFICATION ANALYSIS (First 10 errors)")
print(f"{'='*80}")
errors = []
for i in range(len(df)):
    if y_true_labels[i] != predictions[i]['severity']:
        errors.append({
            'id': df.iloc[i]['incident_id'],
            'description': df.iloc[i]['issue_description'][:80],
            'actual': y_true_labels[i],
            'predicted': predictions[i]['severity'],
            'confidence': predictions[i]['confidence']
        })

if errors:
    print(f"\nTotal misclassifications: {len(errors)} out of {len(df)} ({len(errors)/len(df):.2%})")
    print("\nFirst 10 misclassifications:")
    for i, error in enumerate(errors[:10], 1):
        print(f"\n{i}. {error['id']}")
        print(f"   Description: {error['description']}...")
        print(f"   Actual: {error['actual']} -> Predicted: {error['predicted']} (confidence: {error['confidence']:.2%})")
else:
    print("\n[OK] Perfect predictions! No misclassifications found.")

# Summary
print(f"\n{'='*80}")
print("VALIDATION SUMMARY")
print(f"{'='*80}")
print(f"[OK] Model Type: XGBoost Classifier")
print(f"[OK] Total Incidents Tested: {len(df)}")
print(f"[OK] Overall Accuracy: {accuracy:.2%}")
print(f"[OK] Weighted F1 Score: {f1:.4f}")
print(f"[OK] Correct Predictions: {sum(1 for i in range(len(y_true)) if y_true[i] == y_pred[i])}/{len(y_true)}")
print(f"[OK] Misclassifications: {len(errors)}/{len(df)}")

if accuracy >= 0.90:
    print(f"\n[EXCELLENT!] Model accuracy is {accuracy:.2%} - exceeds 90% threshold")
elif accuracy >= 0.80:
    print(f"\n[GOOD!] Model accuracy is {accuracy:.2%} - meets 80% threshold")
elif accuracy >= 0.70:
    print(f"\n[ACCEPTABLE] Model accuracy is {accuracy:.2%} - room for improvement")
else:
    print(f"\n[WARNING!] Model accuracy is {accuracy:.2%} - consider retraining")

print(f"\n{'='*80}")

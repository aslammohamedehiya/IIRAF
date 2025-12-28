"""
Severity Predictor using XGBoost
Predicts incident severity (Low, Medium, High, Critical) from description text
"""
import os
import sys
import pickle
import pandas as pd
import numpy as np
import xgboost as xgb

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from .ml_utils import MLUtils

class SeverityPredictor:
    """Predict incident severity using XGBoost classifier"""
    
    def __init__(self):
        """Initialize severity predictor"""
        self.model = None
        self.vectorizer = None
        self.label_encoder = {'Low': 0, 'Medium': 1, 'High': 2, 'Critical': 3}
        self.label_decoder = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'}
        self.is_trained = False
        
        # Model paths
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        self.model_path = os.path.join(self.model_dir, "severity_predictor.pkl")
        self.vectorizer_path = os.path.join(self.model_dir, "tfidf_vectorizer.pkl")
        
        # Try to load existing model
        self.load_model()
    
    def train(self, df=None, retrain=False):
        """
        Train the severity prediction model
        
        Args:
            df: DataFrame with 'description' and 'severity' columns (optional)
            retrain: Force retraining even if model exists
            
        Returns:
            Dictionary with training results
        """
        # Skip if already trained and not forcing retrain
        if self.is_trained and not retrain:
            print("[INFO] Model already trained. Use retrain=True to force retraining.")
            return {"status": "already_trained"}
        
        # Load data if not provided
        if df is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            df = pd.read_csv(os.path.join(data_dir, "incidents.csv"))
            
            # Map field names
            if 'issue_description' in df.columns:
                df['description'] = df['issue_description']
        
        print(f"Training on {len(df)} incidents...")
        
        # Prepare features and labels
        X_text = df['description'].fillna('').tolist()
        y = df['severity'].map(self.label_encoder).values
        
        # Convert text to TF-IDF features
        X, self.vectorizer = MLUtils.preprocess_text_tfidf(
            X_text, 
            max_features=200,
            ngram_range=(1, 2)
        )
        
        # Split data
        X_train, X_test, y_train, y_test = MLUtils.split_data(X, y, test_size=0.2)
        
        print(f"Training set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        
        # Train XGBoost model
        self.model = xgb.XGBClassifier(
            objective='multi:softmax',
            num_class=4,
            max_depth=5,
            learning_rate=0.1,
            n_estimators=100,
            random_state=42,
            eval_metric='mlogloss'
        )
        
        print("Training XGBoost model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        results = MLUtils.evaluate_model(
            self.model, 
            X_test, 
            y_test,
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        print(f"\n[OK] Model trained successfully!")
        print(f"Accuracy: {results['accuracy']:.2%}")
        print(f"F1 Score: {results['f1_score']:.2f}")
        
        # Get feature importance
        top_features = MLUtils.get_feature_importance(self.model, self.vectorizer, top_n=10)
        results['top_features'] = top_features
        
        print(f"\nTop 10 important features:")
        for feature, importance in top_features[:10]:
            print(f"  {feature}: {importance:.4f}")
        
        self.is_trained = True
        
        # Add training sample count to results
        results['training_samples'] = X_train.shape[0]  # Use shape[0] for sparse matrices
        
        # Save model with metadata
        self.save_model(training_results=results)
        
        return results
    
    def predict(self, description):
        """
        Predict severity for a single incident description
        
        Args:
            description: Incident description text
            
        Returns:
            Dictionary with prediction and confidence scores
        """
        if not self.is_trained:
            return {
                'error': 'Model not trained. Please train the model first.',
                'severity': 'Unknown',
                'confidence': 0.0
            }
        
        # Preprocess text
        X, _ = MLUtils.preprocess_text_tfidf([description], vectorizer=self.vectorizer)
        
        # Predict
        severity_code = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        severity = self.label_decoder[severity_code]
        confidence = float(probabilities[severity_code])
        
        # Get all probabilities
        all_probs = {
            self.label_decoder[i]: float(prob) 
            for i, prob in enumerate(probabilities)
        }
        
        return {
            'severity': severity,
            'confidence': confidence,
            'probabilities': all_probs,
            'model': 'xgboost'
        }
    
    def predict_batch(self, descriptions):
        """
        Predict severity for multiple descriptions
        
        Args:
            descriptions: List of incident descriptions
            
        Returns:
            List of prediction dictionaries
        """
        if not self.is_trained:
            return [{'error': 'Model not trained'}] * len(descriptions)
        
        # Preprocess all texts
        X, _ = MLUtils.preprocess_text_tfidf(descriptions, vectorizer=self.vectorizer)
        
        # Predict
        severity_codes = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        results = []
        for i, (code, probs) in enumerate(zip(severity_codes, probabilities)):
            severity = self.label_decoder[code]
            confidence = float(probs[code])
            
            results.append({
                'severity': severity,
                'confidence': confidence,
                'probabilities': {
                    self.label_decoder[j]: float(p) 
                    for j, p in enumerate(probs)
                }
            })
        
        return results
    
    def save_model(self, training_results=None):
        """Save trained model and vectorizer to disk with metadata"""
        if not self.is_trained:
            print("[WARNING] No trained model to save")
            return
        
        # Create models directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Save model
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save vectorizer
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # Save metadata
        import json
        from datetime import datetime
        
        metadata_path = os.path.join(self.model_dir, "model_metadata.json")
        metadata = {
            "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_type": "XGBoost Classifier",
            "num_classes": 4,
            "classes": list(self.label_decoder.values())
        }
        
        if training_results:
            metadata.update({
                "accuracy": training_results.get('accuracy', 0),
                "test_accuracy": training_results.get('accuracy', 0),
                "f1_score": training_results.get('f1_score', 0),
                "training_samples": training_results.get('training_samples', 0)
            })
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"[OK] Model and metadata saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model and vectorizer from disk"""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                self.is_trained = True
                print("[OK] Loaded existing severity prediction model")
                return True
            except Exception as e:
                print(f"[WARNING] Failed to load model: {e}")
                return False
        return False
    
    def get_model_info(self):
        """Get information about the trained model"""
        if not self.is_trained:
            return {
                "status": "not_trained",
                "accuracy": 0,
                "training_samples": 0,
                "last_trained": "Unknown"
            }
        
        # Try to load model metadata file
        import os
        import json
        from datetime import datetime
        
        metadata_path = os.path.join(self.model_dir, "model_metadata.json")
        metadata = {}
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load model metadata: {e}")
        
        # Get model file modification time as fallback for last_trained
        last_trained = "Unknown"
        if os.path.exists(self.model_path):
            try:
                mtime = os.path.getmtime(self.model_path)
                last_trained = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        return {
            "status": "trained",
            "model_type": "XGBoost Classifier",
            "num_classes": 4,
            "classes": list(self.label_decoder.values()),
            "num_features": self.vectorizer.max_features if self.vectorizer else 0,
            "model_path": self.model_path,
            "accuracy": metadata.get("accuracy", 0),
            "test_accuracy": metadata.get("test_accuracy", 0),
            "training_samples": metadata.get("training_samples", 0),
            "last_trained": metadata.get("last_trained", last_trained)
        }


if __name__ == "__main__":
    print("="*60)
    print("SEVERITY PREDICTOR - TRAINING AND TESTING")
    print("="*60)
    
    # Initialize predictor
    predictor = SeverityPredictor()
    
    # Train model
    print("\n1. Training model...")
    results = predictor.train(retrain=True)
    
    if 'accuracy' in results:
        print(f"\n2. Model Performance:")
        print(f"   Accuracy: {results['accuracy']:.2%}")
        print(f"   F1 Score: {results['f1_score']:.2f}")
    
    # Test predictions
    print(f"\n3. Testing predictions...")
    
    test_cases = [
        "Critical system outage affecting all users",
        "User unable to login to application",
        "Slow response time in dashboard",
        "Minor UI alignment issue in settings page"
    ]
    
    for desc in test_cases:
        prediction = predictor.predict(desc)
        print(f"\n   Description: {desc[:50]}...")
        print(f"   Predicted: {prediction['severity']} (confidence: {prediction['confidence']:.2%})")
    
    print(f"\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)

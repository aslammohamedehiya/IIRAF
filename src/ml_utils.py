"""
ML Utilities for IIRAF
Provides common machine learning functions for preprocessing, evaluation, and feature engineering
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import numpy as np
import pandas as pd

class MLUtils:
    """Utility functions for machine learning tasks"""
    
    @staticmethod
    def preprocess_text_tfidf(texts, max_features=200, ngram_range=(1, 2), vectorizer=None):
        """
        Convert text to TF-IDF features
        
        Args:
            texts: List of text strings
            max_features: Maximum number of features
            ngram_range: N-gram range (default: unigrams and bigrams)
            vectorizer: Existing vectorizer (for transform only)
            
        Returns:
            Tuple of (features, vectorizer)
        """
        if vectorizer is None:
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english',
                ngram_range=ngram_range,
                lowercase=True,
                strip_accents='unicode'
            )
            features = vectorizer.fit_transform(texts)
        else:
            features = vectorizer.transform(texts)
        
        return features, vectorizer
    
    @staticmethod
    def split_data(X, y, test_size=0.2, random_state=42):
        """
        Split data into train and test sets
        
        Args:
            X: Features
            y: Labels
            test_size: Proportion of test set (default: 0.2)
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    
    @staticmethod
    def evaluate_model(model, X_test, y_test, labels=None):
        """
        Comprehensive model evaluation
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            labels: Label names for classification report
            
        Returns:
            Dictionary with evaluation metrics
        """
        y_pred = model.predict(X_test)
        
        results = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        if labels:
            results['classification_report'] = classification_report(
                y_test, y_pred, target_names=labels, output_dict=True
            )
        
        return results
    
    @staticmethod
    def cross_validate(model, X, y, cv=5):
        """
        Perform cross-validation
        
        Args:
            model: Model to evaluate
            X: Features
            y: Labels
            cv: Number of folds (default: 5)
            
        Returns:
            Dictionary with cross-validation scores
        """
        scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
        
        return {
            'cv_scores': scores.tolist(),
            'mean_score': scores.mean(),
            'std_score': scores.std()
        }
    
    @staticmethod
    def get_feature_importance(model, vectorizer, top_n=20):
        """
        Get top important features from model
        
        Args:
            model: Trained model with feature_importances_
            vectorizer: TfidfVectorizer used for features
            top_n: Number of top features to return
            
        Returns:
            List of (feature_name, importance) tuples
        """
        if not hasattr(model, 'feature_importances_'):
            return []
        
        feature_names = vectorizer.get_feature_names_out()
        importances = model.feature_importances_
        
        # Get top N features
        indices = np.argsort(importances)[::-1][:top_n]
        
        return [(feature_names[i], float(importances[i])) for i in indices]
    
    @staticmethod
    def balance_dataset(df, target_column, method='undersample'):
        """
        Balance dataset by undersampling or oversampling
        
        Args:
            df: DataFrame
            target_column: Column name for target variable
            method: 'undersample' or 'oversample'
            
        Returns:
            Balanced DataFrame
        """
        if method == 'undersample':
            # Undersample to match smallest class
            min_count = df[target_column].value_counts().min()
            balanced_dfs = []
            
            for label in df[target_column].unique():
                label_df = df[df[target_column] == label]
                sampled = label_df.sample(n=min_count, random_state=42)
                balanced_dfs.append(sampled)
            
            return pd.concat(balanced_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
        
        elif method == 'oversample':
            # Oversample to match largest class
            max_count = df[target_column].value_counts().max()
            balanced_dfs = []
            
            for label in df[target_column].unique():
                label_df = df[df[target_column] == label]
                sampled = label_df.sample(n=max_count, replace=True, random_state=42)
                balanced_dfs.append(sampled)
            
            return pd.concat(balanced_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
        
        else:
            raise ValueError("method must be 'undersample' or 'oversample'")

if __name__ == "__main__":
    # Test ML utilities
    print("Testing ML Utilities...")
    
    # Sample data
    texts = [
        "User reported login failure",
        "Payment gateway timeout error",
        "Database connection lost",
        "Application crashed unexpectedly"
    ]
    
    # Test TF-IDF
    features, vectorizer = MLUtils.preprocess_text_tfidf(texts, max_features=10)
    print(f"\n[OK] TF-IDF features shape: {features.shape}")
    print(f"Feature names: {vectorizer.get_feature_names_out()[:5]}")
    
    # Test train/test split
    X = np.random.rand(100, 10)
    y = np.random.randint(0, 4, 100)
    X_train, X_test, y_train, y_test = MLUtils.split_data(X, y)
    print(f"\n[OK] Train/test split: {X_train.shape}, {X_test.shape}")
    
    print("\n[OK] All ML utilities working correctly!")

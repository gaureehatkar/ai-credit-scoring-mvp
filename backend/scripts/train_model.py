"""
Train XGBoost credit scoring model on Give Me Some Credit dataset.

Usage:
    python scripts/train_model.py --data data/cs-training.csv --output models/
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
import joblib
import shap
import os
import argparse


def preprocess_data(df: pd.DataFrame) -> tuple:
    """Preprocess Give Me Some Credit dataset"""
    print("Preprocessing data...")
    
    # Handle missing values
    df['MonthlyIncome'] = df['MonthlyIncome'].fillna(df['MonthlyIncome'].median())
    df['NumberOfDependents'] = df['NumberOfDependents'].fillna(0)
    
    # Remove extreme outliers
    df = df[df['DebtRatio'] <= 10]
    df = df[df['age'] >= 18]
    df = df[df['age'] <= 100]
    
    # Feature engineering
    df['age_squared'] = df['age'] ** 2
    df['debt_ratio_log'] = np.log1p(df['DebtRatio'])
    df['monthly_income_log'] = np.log1p(df['MonthlyIncome'])
    df['total_late_payments'] = (
        df['NumberOfTimes90DaysLate'] + 
        df['NumberOfTime60-89DaysPastDueNotWorse'] +
        df['NumberOfTime30-59DaysPastDueNotWorse']
    )
    df['has_real_estate'] = (df['NumberRealEstateLoansOrLines'] > 0).astype(int)
    
    # Select features
    feature_cols = [
        'age', 'age_squared',
        'DebtRatio', 'debt_ratio_log',
        'MonthlyIncome', 'monthly_income_log',
        'NumberOfOpenCreditLinesAndLoans',
        'NumberOfTimes90DaysLate',
        'NumberRealEstateLoansOrLines',
        'NumberOfTime60-89DaysPastDueNotWorse',
        'NumberOfDependents',
        'total_late_payments',
        'has_real_estate'
    ]
    
    X = df[feature_cols]
    y = df['SeriousDlqin2yrs']
    
    print(f"Dataset shape: {X.shape}")
    print(f"Class distribution: {y.value_counts().to_dict()}")
    
    return X, y, feature_cols


def train_model(X_train, y_train, X_val, y_val):
    """Train XGBoost classifier"""
    print("\nTraining XGBoost model...")
    
    # Calculate class imbalance ratio
    scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])
    print(f"Class imbalance ratio: {scale_pos_weight:.2f}")
    
    # Initialize model
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
        eval_metric='auc'
    )
    
    # Train with early stopping
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=True
    )
    
    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate model performance"""
    print("\nEvaluating model...")
    
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"\nTest AUC-ROC: {auc:.4f}")
    print(f"Target AUC: 0.79")
    print(f"Meets threshold: {auc >= 0.79}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    return auc


def save_artifacts(model, feature_names, output_dir='models'):
    """Save model artifacts"""
    print(f"\nSaving model artifacts to {output_dir}/...")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(output_dir, 'xgboost_model.pkl')
    joblib.dump(model, model_path)
    print(f"✓ Model saved: {model_path}")
    
    # Save feature names
    features_path = os.path.join(output_dir, 'feature_names.pkl')
    joblib.dump(feature_names, features_path)
    print(f"✓ Feature names saved: {features_path}")
    
    # Initialize and save SHAP explainer
    print("Initializing SHAP explainer...")
    explainer = shap.TreeExplainer(model)
    explainer_path = os.path.join(output_dir, 'shap_explainer.pkl')
    joblib.dump(explainer, explainer_path)
    print(f"✓ SHAP explainer saved: {explainer_path}")


def main():
    parser = argparse.ArgumentParser(description='Train credit scoring model')
    parser.add_argument('--data', type=str, required=True, help='Path to training data CSV')
    parser.add_argument('--output', type=str, default='models', help='Output directory for model artifacts')
    args = parser.parse_args()
    
    print("="*80)
    print("AI Credit Scoring Model Training")
    print("="*80)
    
    # Load data
    print(f"\nLoading data from {args.data}...")
    df = pd.read_csv(args.data)
    print(f"Loaded {len(df)} records")
    
    # Preprocess
    X, y, feature_cols = preprocess_data(df)
    
    # Split data
    print("\nSplitting data...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.2, random_state=42, stratify=y_temp
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Validation set: {len(X_val)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train model
    model = train_model(X_train, y_train, X_val, y_val)
    
    # Evaluate
    auc = evaluate_model(model, X_test, y_test)
    
    # Save artifacts
    save_artifacts(model, feature_cols, args.output)
    
    print("\n" + "="*80)
    print("Training Complete!")
    print("="*80)
    print(f"Final AUC: {auc:.4f}")
    print(f"Model ready for deployment: {auc >= 0.79}")


if __name__ == "__main__":
    main()

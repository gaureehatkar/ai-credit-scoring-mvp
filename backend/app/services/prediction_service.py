import numpy as np
import joblib
from typing import Dict, List
from app.schemas.application import CreditApplicationCreate, SHAPExplanation


class FeatureVector:
    def __init__(self, features: Dict[str, float], feature_names: List[str]):
        self.features = features
        self.feature_names = feature_names


class CreditScoreResult:
    def __init__(self, credit_score: float, default_probability: float, 
                 risk_category: str, shap_explanations: List[SHAPExplanation],
                 model_version: str):
        self.credit_score = credit_score
        self.default_probability = default_probability
        self.risk_category = risk_category
        self.shap_explanations = shap_explanations
        self.model_version = model_version


class PredictionService:
    def __init__(self, model_path: str, shap_explainer_path: str, feature_names_path: str):
        """Initialize with pre-trained model"""
        self.model = joblib.load(model_path)
        self.shap_explainer = joblib.load(shap_explainer_path)
        self.expected_features = joblib.load(feature_names_path)
        self.model_version = "xgboost_v1.0"
    
    def engineer_features(self, application_data: CreditApplicationCreate) -> FeatureVector:
        """Extract and engineer features from application data"""
        alt_data = application_data.alternative_data
        
        # Map alternative data to model's expected features
        # The model expects these 13 features from the Kaggle dataset:
        # age, age_squared, DebtRatio, debt_ratio_log, MonthlyIncome, monthly_income_log,
        # NumberOfOpenCreditLinesAndLoans, NumberOfTimes90DaysLate, NumberRealEstateLoansOrLines,
        # NumberOfTime60-89DaysPastDueNotWorse, NumberOfDependents, total_late_payments, has_real_estate
        
        features = {}
        
        # Direct mappings
        features['age'] = float(application_data.age)
        features['age_squared'] = float(application_data.age ** 2)
        features['MonthlyIncome'] = float(alt_data.monthly_income if alt_data.monthly_income else 5000.0)
        features['monthly_income_log'] = float(np.log1p(features['MonthlyIncome']))
        
        # Estimate DebtRatio from requested amount and income
        if features['MonthlyIncome'] > 0:
            features['DebtRatio'] = float(application_data.requested_amount / (features['MonthlyIncome'] * 12))
        else:
            features['DebtRatio'] = 0.5
        features['debt_ratio_log'] = float(np.log1p(features['DebtRatio']))
        
        # Map alternative data to traditional credit features
        if application_data.applicant_type == "underbanked":
            # Use gig rating and UPI frequency to estimate creditworthiness
            gig_rating = alt_data.gig_platform_rating or 3.0
            upi_freq = alt_data.upi_transaction_frequency or 10
            savings = alt_data.savings_account_balance or 0
            
            # Estimate credit lines based on digital activity
            features['NumberOfOpenCreditLinesAndLoans'] = int(max(1, upi_freq / 10))
            
            # Estimate late payments inversely from gig rating (higher rating = fewer late payments)
            features['NumberOfTimes90DaysLate'] = int(max(0, 5 - gig_rating))
            features['NumberOfTime60-89DaysPastDueNotWorse'] = int(max(0, 4 - gig_rating))
            
            # Estimate real estate from savings
            features['NumberRealEstateLoansOrLines'] = 1 if savings > 50000 else 0
            features['has_real_estate'] = 1 if savings > 50000 else 0
            
        elif application_data.applicant_type == "unbanked":
            # Use community score and remittances to estimate creditworthiness
            community_score = alt_data.community_verification_score or 5.0
            remittance_freq = alt_data.remittance_frequency or 0
            microfinance_count = alt_data.microfinance_repayment_count or 0
            
            # Estimate credit lines from microfinance history
            features['NumberOfOpenCreditLinesAndLoans'] = int(max(1, microfinance_count))
            
            # Estimate late payments inversely from community score
            features['NumberOfTimes90DaysLate'] = int(max(0, 10 - community_score))
            features['NumberOfTime60-89DaysPastDueNotWorse'] = int(max(0, 8 - community_score))
            
            # No real estate for unbanked
            features['NumberRealEstateLoansOrLines'] = 0
            features['has_real_estate'] = 0
        
        # Estimate dependents (default to 2)
        features['NumberOfDependents'] = 2
        
        # Calculate total late payments
        features['total_late_payments'] = (
            features['NumberOfTimes90DaysLate'] + 
            features['NumberOfTime60-89DaysPastDueNotWorse']
        )
        
        # Ensure all features are in the correct order matching the trained model
        feature_names = self.expected_features
        
        return FeatureVector(features=features, feature_names=feature_names)
    
    def predict_credit_score(self, features: FeatureVector) -> CreditScoreResult:
        """Predict credit score and generate SHAP explanations"""
        # Prepare feature array
        feature_array = np.array([features.features[name] for name in features.feature_names])
        feature_array = feature_array.reshape(1, -1)
        
        # Predict default probability
        default_probability = float(self.model.predict_proba(feature_array)[0, 1])
        
        # Convert to credit score (300-850 scale)
        credit_score = 300 + (850 - 300) * (1 - default_probability)
        credit_score = float(np.clip(credit_score, 300, 850))
        
        # Determine risk category
        risk_category = self.calculate_risk_category(credit_score)
        
        # Generate SHAP explanations
        shap_explanations = self.generate_shap_explanation(features, feature_array)
        
        return CreditScoreResult(
            credit_score=credit_score,
            default_probability=default_probability,
            risk_category=risk_category,
            shap_explanations=shap_explanations,
            model_version=self.model_version
        )
    
    def calculate_risk_category(self, credit_score: float) -> str:
        """Categorize risk based on credit score"""
        if credit_score >= 700:
            return "low"
        elif credit_score >= 600:
            return "medium"
        else:
            return "high"
    
    def generate_shap_explanation(self, features: FeatureVector, feature_array: np.ndarray) -> List[SHAPExplanation]:
        """Generate SHAP values for model transparency"""
        try:
            shap_values = self.shap_explainer.shap_values(feature_array)
            
            # Create explanations for all features
            feature_importance = []
            for i, feature_name in enumerate(features.feature_names):
                shap_value = float(shap_values[0][i])
                feature_value = float(features.features[feature_name])
                impact = "positive" if shap_value > 0 else "negative"
                
                feature_importance.append(
                    SHAPExplanation(
                        feature_name=feature_name,
                        feature_value=feature_value,
                        shap_value=shap_value,
                        impact=impact
                    )
                )
            
            # Sort by absolute SHAP value and take top 10
            feature_importance.sort(key=lambda x: abs(x.shap_value), reverse=True)
            return feature_importance[:10]
        
        except Exception as e:
            print(f"SHAP explanation failed: {e}")
            return []

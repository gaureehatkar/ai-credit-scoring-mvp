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
        
        # The model expects these 13 features from the Kaggle dataset:
        # age, age_squared, DebtRatio, debt_ratio_log, MonthlyIncome, monthly_income_log,
        # NumberOfOpenCreditLinesAndLoans, NumberOfTimes90DaysLate, NumberRealEstateLoansOrLines,
        # NumberOfTime60-89DaysPastDueNotWorse, NumberOfDependents, total_late_payments, has_real_estate
        
        features = {}
        
        # --- Age ---
        features['age'] = float(application_data.age)
        features['age_squared'] = float(application_data.age ** 2)

        # --- Income & Expenses ---
        monthly_income = float(alt_data.monthly_income or 5000.0)
        monthly_expenses = float(alt_data.monthly_expenses or monthly_income * 0.6)
        disposable_income = max(monthly_income - monthly_expenses, 0)
        features['MonthlyIncome'] = monthly_income
        features['monthly_income_log'] = float(np.log1p(monthly_income))

        # --- Debt Ratio: use existing loans + requested amount vs annual income ---
        existing_loan_count = int(alt_data.existing_loan_count or 0)
        # Estimate existing monthly debt obligation (avg ₹5000 per loan)
        estimated_existing_debt = existing_loan_count * 5000
        total_monthly_debt = estimated_existing_debt + (application_data.requested_amount / 36)
        if monthly_income > 0:
            features['DebtRatio'] = float(total_monthly_debt / monthly_income)
        else:
            features['DebtRatio'] = 1.0
        features['debt_ratio_log'] = float(np.log1p(features['DebtRatio']))

        # --- Dependents ---
        features['NumberOfDependents'] = int(alt_data.number_of_dependents if alt_data.number_of_dependents is not None else 2)

        # --- Employment stability bonus/penalty ---
        # More years in employment = more stable = fewer estimated late payments
        stability_years = float(alt_data.employment_stability_years or 1.0)
        stability_factor = min(stability_years / 5.0, 1.0)  # caps at 1.0 after 5 years

        # --- Utility bill payment score (0-10) ---
        utility_score = float(alt_data.utility_bill_payment_score or 5.0)

        # --- Loan repayment history score (0-10) ---
        repayment_score = float(alt_data.loan_repayment_history_score or 5.0)

        # --- Map alternative data to traditional credit features ---
        if application_data.applicant_type == "underbanked":
            gig_rating = float(alt_data.gig_platform_rating or 3.0)
            upi_freq = int(alt_data.upi_transaction_frequency or 10)
            savings = float(alt_data.savings_account_balance or 0)

            # Credit lines: UPI activity + existing loans
            features['NumberOfOpenCreditLinesAndLoans'] = int(max(1, upi_freq / 10 + existing_loan_count))

            # Late payments: inversely from gig rating + repayment history + utility score
            combined_behavior_score = (gig_rating / 5.0 * 4 + repayment_score / 10.0 * 3 + utility_score / 10.0 * 3)
            features['NumberOfTimes90DaysLate'] = int(max(0, round((1 - combined_behavior_score / 10) * 5 * (1 - stability_factor * 0.3))))
            features['NumberOfTime60-89DaysPastDueNotWorse'] = int(max(0, round((1 - combined_behavior_score / 10) * 4 * (1 - stability_factor * 0.3))))

            # Real estate from savings
            features['NumberRealEstateLoansOrLines'] = 1 if savings > 50000 else 0
            features['has_real_estate'] = 1 if savings > 50000 else 0

        elif application_data.applicant_type == "unbanked":
            community_score = float(alt_data.community_verification_score or 5.0)
            remittance_freq = int(alt_data.remittance_frequency or 0)
            microfinance_count = int(alt_data.microfinance_repayment_count or 0)

            # Credit lines: microfinance + existing loans
            features['NumberOfOpenCreditLinesAndLoans'] = int(max(1, microfinance_count + existing_loan_count))

            # Late payments: from community score + repayment history + utility score
            combined_behavior_score = (community_score / 10.0 * 4 + repayment_score / 10.0 * 3 + utility_score / 10.0 * 3)
            features['NumberOfTimes90DaysLate'] = int(max(0, round((1 - combined_behavior_score / 10) * 8 * (1 - stability_factor * 0.3))))
            features['NumberOfTime60-89DaysPastDueNotWorse'] = int(max(0, round((1 - combined_behavior_score / 10) * 6 * (1 - stability_factor * 0.3))))

            features['NumberRealEstateLoansOrLines'] = 0
            features['has_real_estate'] = 0

        # --- Total late payments ---
        features['total_late_payments'] = (
            features['NumberOfTimes90DaysLate'] +
            features['NumberOfTime60-89DaysPastDueNotWorse']
        )

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

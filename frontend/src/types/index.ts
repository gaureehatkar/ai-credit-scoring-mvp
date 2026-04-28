export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  role: string;
}

export interface AlternativeData {
  monthly_income?: number;
  monthly_expenses?: number;
  utility_payment_history?: string;
  employment_type?: string;
  employment_stability_years?: number;
  number_of_dependents?: number;
  existing_loan_count?: number;
  loan_repayment_history_score?: number;
  utility_bill_payment_score?: number;
  remittance_frequency?: number;
  community_verification_score?: number;
  microfinance_repayment_count?: number;
  gig_platform_rating?: number;
  upi_transaction_frequency?: number;
  savings_account_balance?: number;
}

export interface CreditApplication {
  applicant_type: 'unbanked' | 'underbanked';
  full_name: string;
  age: number;
  phone_number: string;
  address: string;
  requested_amount: number;
  loan_purpose: string;
  alternative_data: AlternativeData;
  document_links?: Record<string, string>;
}

export interface ApplicationResponse {
  application_id: number;
  user_id: number;
  applicant_type: string;
  status: string;
  requested_amount: number;
  credit_score?: number;
  risk_category?: string;
  created_at: string;
  updated_at: string;
}

export interface SHAPExplanation {
  feature_name: string;
  feature_value: number;
  shap_value: number;
  impact: string;
}

export interface CreditScoreDetail {
  application_id: number;
  credit_score: number;
  default_probability: number;
  risk_category: string;
  shap_explanations: SHAPExplanation[];
  model_version: string;
  created_at: string;
}

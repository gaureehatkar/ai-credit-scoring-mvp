import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { submitApplication } from '../services/api';
import type { CreditApplication, AlternativeData } from '../types';

function ApplicationPage() {
  const navigate = useNavigate();
  const [applicantType, setApplicantType] = useState<'unbanked' | 'underbanked'>('underbanked');
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState(25);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [address, setAddress] = useState('');
  const [requestedAmount, setRequestedAmount] = useState(50000);
  const [loanPurpose, setLoanPurpose] = useState('');
  
  const [altData, setAltData] = useState<AlternativeData>({
    monthly_income: 25000,
    employment_type: 'gig_worker',
    gig_platform_rating: 4.5,
    upi_transaction_frequency: 30,
    savings_account_balance: 10000
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const application: CreditApplication = {
      applicant_type: applicantType,
      full_name: fullName,
      age,
      phone_number: phoneNumber,
      address,
      requested_amount: requestedAmount,
      loan_purpose: loanPurpose,
      alternative_data: altData
    };

    try {
      const response = await submitApplication(application);
      setResult(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Application submission failed');
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div>
        <div className="navbar">
          <h1>AI Credit Scoring Platform</h1>
          <button onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
        </div>
        <div className="container" style={{ maxWidth: '600px' }}>
          <div className="card">
            <div className="score-display">
              <h2>Your Credit Score</h2>
              <div className="score-value">{Math.round(result.credit_score || 0)}</div>
              <div className={`risk-badge risk-${result.risk_category}`}>
                {result.risk_category?.toUpperCase()} RISK
              </div>
              <div style={{ marginTop: '24px' }}>
                <p><strong>Status:</strong> {result.status.replace('_', ' ').toUpperCase()}</p>
                <p><strong>Application ID:</strong> {result.application_id}</p>
              </div>
            </div>
            <button onClick={() => navigate('/dashboard')} style={{ width: '100%' }}>
              View All Applications
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="navbar">
        <h1>AI Credit Scoring Platform</h1>
        <button onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
      </div>
      <div className="container" style={{ maxWidth: '800px' }}>
        <div className="card">
          <h2 style={{ marginBottom: '24px' }}>Credit Application</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Applicant Type</label>
              <select value={applicantType} onChange={(e) => setApplicantType(e.target.value as any)}>
                <option value="underbanked">Underbanked</option>
                <option value="unbanked">Unbanked</option>
              </select>
            </div>

            <div className="form-group">
              <label>Full Name</label>
              <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            </div>

            <div className="form-group">
              <label>Age</label>
              <input type="number" value={age} onChange={(e) => setAge(Number(e.target.value))} min={18} max={100} required />
            </div>

            <div className="form-group">
              <label>Phone Number</label>
              <input type="tel" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} required />
            </div>

            <div className="form-group">
              <label>Address</label>
              <textarea value={address} onChange={(e) => setAddress(e.target.value)} required rows={3} />
            </div>

            <div className="form-group">
              <label>Requested Amount (₹)</label>
              <input type="number" value={requestedAmount} onChange={(e) => setRequestedAmount(Number(e.target.value))} min={1000} required />
            </div>

            <div className="form-group">
              <label>Loan Purpose</label>
              <input type="text" value={loanPurpose} onChange={(e) => setLoanPurpose(e.target.value)} required />
            </div>

            <h3 style={{ marginTop: '24px', marginBottom: '16px' }}>Alternative Data</h3>

            <div className="form-group">
              <label>Monthly Income (₹)</label>
              <input 
                type="number" 
                value={altData.monthly_income || ''} 
                onChange={(e) => setAltData({...altData, monthly_income: Number(e.target.value)})} 
              />
            </div>

            {applicantType === 'underbanked' && (
              <>
                <div className="form-group">
                  <label>Gig Platform Rating (0-5)</label>
                  <input 
                    type="number" 
                    step="0.1"
                    value={altData.gig_platform_rating || ''} 
                    onChange={(e) => setAltData({...altData, gig_platform_rating: Number(e.target.value)})} 
                    min={0} max={5}
                  />
                </div>
                <div className="form-group">
                  <label>UPI Transactions per Month</label>
                  <input 
                    type="number" 
                    value={altData.upi_transaction_frequency || ''} 
                    onChange={(e) => setAltData({...altData, upi_transaction_frequency: Number(e.target.value)})} 
                  />
                </div>
                <div className="form-group">
                  <label>Savings Account Balance (₹)</label>
                  <input 
                    type="number" 
                    value={altData.savings_account_balance || ''} 
                    onChange={(e) => setAltData({...altData, savings_account_balance: Number(e.target.value)})} 
                  />
                </div>
              </>
            )}

            {applicantType === 'unbanked' && (
              <>
                <div className="form-group">
                  <label>Remittance Frequency (per year)</label>
                  <input 
                    type="number" 
                    value={altData.remittance_frequency || ''} 
                    onChange={(e) => setAltData({...altData, remittance_frequency: Number(e.target.value)})} 
                  />
                </div>
                <div className="form-group">
                  <label>Community Verification Score (0-10)</label>
                  <input 
                    type="number" 
                    step="0.1"
                    value={altData.community_verification_score || ''} 
                    onChange={(e) => setAltData({...altData, community_verification_score: Number(e.target.value)})} 
                    min={0} max={10}
                  />
                </div>
                <div className="form-group">
                  <label>Microfinance Repayment Count</label>
                  <input 
                    type="number" 
                    value={altData.microfinance_repayment_count || ''} 
                    onChange={(e) => setAltData({...altData, microfinance_repayment_count: Number(e.target.value)})} 
                  />
                </div>
              </>
            )}

            {error && <div className="error">{error}</div>}
            <button type="submit" disabled={loading} style={{ width: '100%', marginTop: '24px' }}>
              {loading ? 'Processing...' : 'Submit Application'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ApplicationPage;

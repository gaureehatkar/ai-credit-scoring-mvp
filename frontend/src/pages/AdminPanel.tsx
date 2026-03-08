import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllApplications, getStatistics } from '../services/api';
import type { ApplicationResponse } from '../types';

function AdminPanel() {
  const [applications, setApplications] = useState<ApplicationResponse[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [appsData, statsData] = await Promise.all([
        getAllApplications(),
        getStatistics()
      ]);
      setApplications(appsData);
      setStatistics(statsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div>
      <div className="navbar">
        <h1>Admin Panel</h1>
        <button onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
      </div>

      <div className="container">
        {statistics && (
          <div className="card">
            <h2 style={{ marginBottom: '24px' }}>Platform Statistics</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div>
                <p style={{ color: '#666', fontSize: '14px' }}>Total Applications</p>
                <p style={{ fontSize: '32px', fontWeight: 'bold' }}>{statistics.total_applications}</p>
              </div>
              <div>
                <p style={{ color: '#666', fontSize: '14px' }}>Approved</p>
                <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#4CAF50' }}>{statistics.approved}</p>
              </div>
              <div>
                <p style={{ color: '#666', fontSize: '14px' }}>Rejected</p>
                <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#f44336' }}>{statistics.rejected}</p>
              </div>
              <div>
                <p style={{ color: '#666', fontSize: '14px' }}>Under Review</p>
                <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#FF9800' }}>{statistics.under_review}</p>
              </div>
              <div>
                <p style={{ color: '#666', fontSize: '14px' }}>Avg Credit Score</p>
                <p style={{ fontSize: '32px', fontWeight: 'bold' }}>{Math.round(statistics.average_credit_score)}</p>
              </div>
              <div>
                <p style={{ color: '#666', fontSize: '14px' }}>Total Users</p>
                <p style={{ fontSize: '32px', fontWeight: 'bold' }}>{statistics.total_users}</p>
              </div>
            </div>
          </div>
        )}

        <div className="card">
          <h2 style={{ marginBottom: '24px' }}>All Applications</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>User ID</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Score</th>
                <th>Risk</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {applications.map((app) => (
                <tr key={app.application_id}>
                  <td>{app.application_id}</td>
                  <td>{app.user_id}</td>
                  <td style={{ textTransform: 'capitalize' }}>{app.applicant_type}</td>
                  <td>₹{app.requested_amount.toLocaleString()}</td>
                  <td>{app.credit_score ? Math.round(app.credit_score) : '-'}</td>
                  <td style={{ textTransform: 'capitalize' }}>{app.risk_category || '-'}</td>
                  <td style={{ textTransform: 'capitalize' }}>{app.status.replace('_', ' ')}</td>
                  <td>{new Date(app.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminPanel;

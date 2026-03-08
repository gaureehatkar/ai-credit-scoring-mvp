import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getApplications, getCurrentUser } from '../services/api';
import type { ApplicationResponse } from '../types';

function Dashboard() {
  const [applications, setApplications] = useState<ApplicationResponse[]>([]);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [userData, appsData] = await Promise.all([
        getCurrentUser(),
        getApplications()
      ]);
      setUser(userData);
      setApplications(appsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_role');
    navigate('/login');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#4CAF50';
      case 'rejected': return '#f44336';
      case 'under_review': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  if (loading) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div>
      <div className="navbar">
        <h1>AI Credit Scoring Platform</h1>
        <nav>
          <span style={{ marginRight: '20px' }}>Welcome, {user?.full_name}</span>
          {user?.role === 'admin' && <Link to="/admin">Admin Panel</Link>}
          <button onClick={handleLogout} style={{ marginLeft: '20px', padding: '8px 16px' }}>
            Logout
          </button>
        </nav>
      </div>

      <div className="container">
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h2>My Applications</h2>
            <Link to="/apply">
              <button>New Application</button>
            </Link>
          </div>

          {applications.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#666', padding: '32px' }}>
              No applications yet. Click "New Application" to get started.
            </p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Credit Score</th>
                  <th>Risk</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.application_id}>
                    <td>{app.application_id}</td>
                    <td style={{ textTransform: 'capitalize' }}>{app.applicant_type}</td>
                    <td>₹{app.requested_amount.toLocaleString()}</td>
                    <td>{app.credit_score ? Math.round(app.credit_score) : '-'}</td>
                    <td style={{ textTransform: 'capitalize' }}>{app.risk_category || '-'}</td>
                    <td>
                      <span style={{ 
                        color: getStatusColor(app.status),
                        fontWeight: '500',
                        textTransform: 'capitalize'
                      }}>
                        {app.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>{new Date(app.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

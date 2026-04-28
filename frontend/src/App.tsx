import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ApplicationPage from './pages/ApplicationPage';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import AdminApplications from './pages/AdminApplications';
import AdminUsers from './pages/AdminUsers';
import AdminAnalytics from './pages/AdminAnalytics';
import VerifyEmail from './pages/VerifyEmail';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('jwt_token');
  return token ? <>{children}</> : <Navigate to="/login" />;
}

function AdminAuthRoute({ children }: { children: React.ReactNode }) {
  const adminToken = localStorage.getItem('admin_token');
  if (!adminToken) return <Navigate to="/admin/login" replace />;
  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('jwt_token');
  return !token ? <>{children}</> : <Navigate to="/dashboard" />;
}

function AdminPublicRoute({ children }: { children: React.ReactNode }) {
  localStorage.removeItem('admin_token');
  localStorage.removeItem('admin_id');
  localStorage.removeItem('admin_email');
  localStorage.removeItem('admin_role');
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/apply" element={<ProtectedRoute><ApplicationPage /></ProtectedRoute>} />

        <Route path="/admin/login" element={<AdminPublicRoute><AdminLogin /></AdminPublicRoute>} />
        <Route path="/admin/dashboard" element={<AdminAuthRoute><AdminDashboard /></AdminAuthRoute>} />
        <Route path="/admin/applications" element={<AdminAuthRoute><AdminApplications /></AdminAuthRoute>} />
        <Route path="/admin/users" element={<AdminAuthRoute><AdminUsers /></AdminAuthRoute>} />
        <Route path="/admin/analytics" element={<AdminAuthRoute><AdminAnalytics /></AdminAuthRoute>} />

        <Route path="/" element={<Navigate to={localStorage.getItem('jwt_token') ? "/dashboard" : "/login"} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

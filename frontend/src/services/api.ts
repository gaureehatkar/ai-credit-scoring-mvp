import axios from 'axios';
import type { TokenResponse, CreditApplication, ApplicationResponse, CreditScoreDetail } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests - only if not already set
api.interceptors.request.use((config) => {
  if (!config.headers.Authorization) {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 responses - clear stale tokens
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || '';
      if (url.includes('/admin/')) {
        // Clear admin token on 401 so the redirect loop breaks
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_id');
        localStorage.removeItem('admin_email');
        localStorage.removeItem('admin_role');
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const register = async (email: string, password: string, full_name: string): Promise<any> => {
  const response = await api.post('/api/v1/auth/register', { email, password, full_name, role: 'applicant' });
  return response.data;
};

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const response = await api.post('/api/v1/auth/login', { email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/v1/auth/me');
  return response.data;
};

// Application API
export const submitApplication = async (application: CreditApplication): Promise<ApplicationResponse> => {
  const response = await api.post('/api/v1/applications', application);
  return response.data;
};

export const getApplications = async (): Promise<ApplicationResponse[]> => {
  const response = await api.get('/api/v1/applications');
  return response.data;
};

export const getApplication = async (applicationId: number): Promise<ApplicationResponse> => {
  const response = await api.get(`/api/v1/applications/${applicationId}`);
  return response.data;
};

export const getCreditScore = async (applicationId: number): Promise<CreditScoreDetail> => {
  const response = await api.get(`/api/v1/applications/${applicationId}/score`);
  return response.data;
};

// Admin API (legacy - kept for backward compatibility)
export const getAllApplications = async (): Promise<ApplicationResponse[]> => {
  const response = await api.get('/api/v1/admin/applications');
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/api/v1/admin/statistics');
  return response.data;
};

// Admin Auth API
export const adminLogin = async (email: string, password: string) => {
  const response = await api.post('/api/v1/admin/auth/login', { email, password });
  return response.data;
};

export const getAdminInfo = async () => {
  const token = localStorage.getItem('admin_token');
  const response = await api.get('/api/v1/admin/auth/me', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

// Admin Applications API
export const getAdminApplications = async (skip: number = 0, limit: number = 100, status?: string) => {
  const token = localStorage.getItem('admin_token');
  const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
  if (status) params.append('status', status);
  
  const response = await api.get(`/api/v1/admin/applications?${params.toString()}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const updateApplicationStatus = async (
  applicationId: number, 
  status: string, 
  notes?: string, 
  reason?: string
) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.patch(
    `/api/v1/admin/applications/${applicationId}/status`,
    { status, notes, reason },
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
  return response.data;
};

// Admin Users API
export const getAdminUsers = async (skip: number = 0, limit: number = 100) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.get(`/api/v1/admin/users?skip=${skip}&limit=${limit}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const createAdminUser = async (data: {
  email: string;
  password: string;
  full_name: string;
  role: string;
  permissions: string[];
}) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.post('/api/v1/admin/users', data, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const updateAdminUser = async (
  adminId: number,
  data: {
    full_name?: string;
    role?: string;
    permissions?: string[];
  }
) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.patch(`/api/v1/admin/users/${adminId}`, data, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const deactivateAdminUser = async (adminId: number) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.delete(`/api/v1/admin/users/${adminId}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

// Admin Analytics API
export const getDashboardMetrics = async (days: number = 30) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.get(`/api/v1/admin/analytics/dashboard?days=${days}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export const getCreditScoreDistribution = async (days: number = 30) => {
  const token = localStorage.getItem('admin_token');
  const response = await api.get(`/api/v1/admin/analytics/credit-score-distribution?days=${days}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export default api;

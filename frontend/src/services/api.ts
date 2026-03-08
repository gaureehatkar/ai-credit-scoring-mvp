import axios from 'axios';
import type { TokenResponse, CreditApplication, ApplicationResponse, CreditScoreDetail } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const register = async (email: string, password: string, full_name: string): Promise<TokenResponse> => {
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

// Admin API
export const getAllApplications = async (): Promise<ApplicationResponse[]> => {
  const response = await api.get('/api/v1/admin/applications');
  return response.data;
};

export const updateApplicationStatus = async (applicationId: number, status: string): Promise<ApplicationResponse> => {
  const response = await api.put(`/api/v1/admin/applications/${applicationId}/status`, { status });
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/api/v1/admin/statistics');
  return response.data;
};

export default api;

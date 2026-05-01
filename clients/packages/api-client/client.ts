"""API client for PaperNormAI backend."""

import axios from 'axios';
import type {
  DocumentResponse,
  DocumentListResponse,
  TemplateResponse,
  TemplateListResponse,
  ValidationResponse,
  ValidationCreateRequest,
  TokenResponse,
  UserResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.error?.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

// Auth API
export const authAPI = {
  register: (email: string, password: string, nickname?: string) =>
    apiClient.post<UserResponse>('/auth/register', { email, password, nickname }),

  login: (email: string, password: string) =>
    apiClient.post<TokenResponse>('/auth/login', { email, password }),
};

// Document API
export const documentAPI = {
  upload: (file: File, templateId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (templateId) {
      formData.append('template_id', templateId);
    }
    return apiClient.post<DocumentResponse>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  list: (page = 1, pageSize = 20, status?: string) =>
    apiClient.get<DocumentListResponse>('/documents/', {
      params: { page, page_size: pageSize, status },
    }),

  get: (documentId: string) =>
    apiClient.get<DocumentResponse>(`/documents/${documentId}`),

  download: (documentId: string) =>
    apiClient.get(`/documents/${documentId}/download`, {
      responseType: 'blob',
    }),
};

// Template API
export const templateAPI = {
  list: (university?: string, degreeType?: string) =>
    apiClient.get<TemplateListResponse>('/templates/', {
      params: { university, degree_type: degreeType },
    }),

  get: (templateId: string) =>
    apiClient.get<TemplateResponse>(`/templates/${templateId}`),
};

// Validation API
export const validationAPI = {
  create: (request: ValidationCreateRequest) =>
    apiClient.post<{ job_id: string; status: string }>('/validations/', request),

  get: (jobId: string) =>
    apiClient.get<ValidationResponse>(`/validations/${jobId}`),
};

export default apiClient;
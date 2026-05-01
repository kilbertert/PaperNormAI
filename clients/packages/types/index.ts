"""TypeScript type definitions for PaperNormAI API client."""

export interface DocumentResponse {
  id: string;
  original_filename: string;
  file_hash: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  template_id?: string;
  uploaded_at: string;
}

export interface DocumentListResponse {
  items: DocumentResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface TemplateRule {
  id: string;
  name: string;
  level: 'L1' | 'L2' | 'L3';
  description: string;
  auto_fixable: boolean;
}

export interface TemplateResponse {
  id: string;
  university: string;
  degree_type: 'bachelor' | 'master' | 'doctor';
  discipline: string;
  version: string;
  is_active: boolean;
  rules: TemplateRule[];
}

export interface TemplateListResponse {
  items: TemplateResponse[];
  total: number;
}

export interface ValidationResultItem {
  id: string;
  rule_id: string;
  severity: 'error' | 'warning' | 'info';
  element_path: string;
  expected_value: string;
  actual_value: string;
  auto_fixable: boolean;
  ai_enhanced: boolean;
}

export interface ValidationSummary {
  total: number;
  errors: number;
  warnings: number;
  infos: number;
  auto_fixable: number;
}

export interface ValidationResponse {
  id: string;
  document_id: string;
  template_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  results: ValidationResultItem[];
  summary?: ValidationSummary;
}

export interface ValidationCreateRequest {
  document_id: string;
  template_id: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string;
  nickname?: string;
  role: string;
  created_at: string;
}
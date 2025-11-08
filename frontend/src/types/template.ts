export interface AutomationTemplate {
  id: number;
  name: string;
  description?: string;
  account_id?: number;
  headless: boolean;
  job_id?: string;
  job_name?: string;
  filters?: any;
  greeting_count: number;
  expected_positions?: string[];
  usage_count: number;
  created_at: string;
  updated_at: string;
  last_used_at?: string;
}

export interface CreateTemplateData {
  name: string;
  description?: string;
  account_id?: number;
  headless: boolean;
  job_id?: string;
  job_name?: string;
  filters?: any;
  greeting_count: number;
  expected_positions?: string[];
}

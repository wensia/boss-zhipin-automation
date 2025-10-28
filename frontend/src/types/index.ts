/**
 * 类型定义
 */

export type CandidateStatus =
  | 'new'
  | 'contacted'
  | 'replied'
  | 'interested'
  | 'rejected'
  | 'archived';

export type TaskStatus =
  | 'pending'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface Candidate {
  id: number;
  boss_id: string;
  name: string;
  position: string;
  company?: string;
  status: CandidateStatus;
  profile_url?: string;
  active_time?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CandidateCreate {
  boss_id: string;
  name: string;
  position: string;
  company?: string;
  status: CandidateStatus;
  profile_url?: string;
  active_time?: string;
  notes?: string;
}

export interface CandidateUpdate {
  status?: CandidateStatus;
  notes?: string;
}

export interface GreetingRecord {
  id: number;
  candidate_id: number;
  task_id?: number;
  template_id?: number;
  message: string;
  success: boolean;
  error_message?: string;
  sent_at: string;
}

export interface AutomationTask {
  id: number;
  search_keywords: string;
  filters?: string;
  greeting_template_id: number;
  max_contacts: number;
  delay_min: number;
  delay_max: number;
  status: TaskStatus;
  progress: number;
  total_found: number;
  total_contacted: number;
  total_success: number;
  total_failed: number;
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface AutomationTaskCreate {
  search_keywords: string;
  filters?: string;
  greeting_template_id: number;
  max_contacts?: number;
  delay_min?: number;
  delay_max?: number;
}

export interface GreetingTemplate {
  id: number;
  name: string;
  content: string;
  is_active: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface GreetingTemplateCreate {
  name: string;
  content: string;
  is_active?: boolean;
}

export interface GreetingTemplateUpdate {
  name?: string;
  content?: string;
  is_active?: boolean;
}

export interface SystemConfig {
  id: number;
  boss_username?: string;
  boss_session_saved: boolean;
  auto_mode_enabled: boolean;
  daily_limit: number;
  today_contacted: number;
  anti_detection_enabled: boolean;
  random_delay_enabled: boolean;
  rest_interval: number;
  rest_duration: number;
  last_contact_time?: string;
  created_at: string;
  updated_at: string;
}

export interface SystemConfigUpdate {
  daily_limit?: number;
  auto_mode_enabled?: boolean;
  anti_detection_enabled?: boolean;
  random_delay_enabled?: boolean;
  rest_interval?: number;
  rest_duration?: number;
}

export interface CandidateStats {
  total: number;
  today_added: number;
  by_status: Record<CandidateStatus, number>;
}

export interface SystemStats {
  config: {
    auto_mode_enabled: boolean;
    daily_limit: number;
    today_contacted: number;
    remaining_today: number;
    boss_session_saved: boolean;
    anti_detection_enabled: boolean;
  };
  candidates: {
    total: number;
    today_added: number;
  };
  greetings: {
    total: number;
    success: number;
    success_rate: number;
    today: number;
  };
  tasks: {
    total: number;
    running: number;
    completed: number;
  };
  templates: {
    total: number;
    active: number;
  };
}

export interface AutomationStatus {
  service_initialized: boolean;
  is_logged_in: boolean;
  current_task_id?: number;
}

export interface UserInfo {
  userId?: number;
  name?: string;
  showName?: string;
  avatar?: string;
  email?: string;
  brandName?: string;
  encryptUserId?: string;
  encryptComId?: string;
}

export type LogLevel = 'debug' | 'info' | 'warning' | 'error' | 'critical';

export type LogAction =
  | 'task_create'
  | 'task_start'
  | 'task_pause'
  | 'task_resume'
  | 'task_complete'
  | 'task_fail'
  | 'task_cancel'
  | 'login_init'
  | 'login_qrcode_get'
  | 'login_qrcode_refresh'
  | 'login_check'
  | 'login_success'
  | 'login_fail'
  | 'candidate_search'
  | 'candidate_contact'
  | 'candidate_contact_success'
  | 'candidate_contact_fail'
  | 'system_init'
  | 'system_cleanup'
  | 'system_error';

export interface LogEntry {
  id: number;
  level: LogLevel;
  action: LogAction;
  message: string;
  details?: string;
  task_id?: number;
  task_name?: string;
  user_id?: string;
  user_name?: string;
  created_at: string;
}

export interface LogsResponse {
  logs: LogEntry[];
  total: number;
  limit: number;
  offset: number;
}

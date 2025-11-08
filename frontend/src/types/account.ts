/**
 * 用户账号类型定义
 */

export interface UserAccount {
  id: number;
  com_id: number;
  name: string;
  show_name: string;
  gender: number;
  avatar: string;
  title: string;
  company_name: string;
  company_short_name: string;
  brand_id: number;
  encrypt_brand_id: string;
  company_logo: string;
  industry: string;
  resume_email: string | null;
  weixin: string | null;
  cert: boolean;
  cert_gender: number;
  is_gold: number;
  raw_data: string;
  last_login_at: string;
  created_at: string;
  updated_at: string;
}

export interface UserAccountCreate {
  com_id: number;
  name: string;
  show_name: string;
  gender: number;
  avatar: string;
  title: string;
  company_name: string;
  company_short_name: string;
  brand_id: number;
  encrypt_brand_id: string;
  company_logo: string;
  industry: string;
  resume_email?: string | null;
  weixin?: string | null;
  cert: boolean;
  cert_gender: number;
  is_gold: number;
  raw_data: string;
  last_login_at: string;
}

export interface UserAccountUpdate {
  name?: string;
  show_name?: string;
  avatar?: string;
  title?: string;
  company_name?: string;
  company_short_name?: string;
  company_logo?: string;
  industry?: string;
  resume_email?: string | null;
  weixin?: string | null;
  cert?: boolean;
  is_gold?: number;
  raw_data?: string;
  last_login_at?: string;
}

/**
 * Boss直聘筛选条件类型定义
 */

export interface FilterOptions {
  // 年龄范围
  age?: {
    min: number;
    max?: number;
  };

  // 专业（可多选）
  major?: string[];

  // 活跃度（单选）
  activity?: '不限' | '刚刚活跃' | '今日活跃' | '3日内活跃' | '本周活跃' | '本月活跃';

  // 性别（可多选）
  gender?: string[];

  // 近期没有看过（可多选）
  notRecentlyViewed?: string[];

  // 是否与同事交换简历（可多选）
  resumeExchange?: string[];

  // 院校（可多选）
  school?: string[];

  // 跳槽频率（单选）
  jobHoppingFrequency?: '不限' | '5年少于3份' | '平均每份工作大于1年';

  // 牛人关键词（可多选）
  keywords?: string[];

  // 经验要求（可多选）
  experience?: string[];

  // 学历要求（可多选）
  education?: string[];

  // 薪资待遇（单选）
  salary?: '不限' | '3K以下' | '3-5K' | '5-10K' | '10-20K' | '20-50K' | '50K以上';

  // 求职意向（可多选）
  jobIntention?: string[];
}

export const FILTER_CONFIG = {
  major: {
    label: '专业',
    type: 'multi-select',
    options: [
      '不限',
      '财会类',
      '电子商务类',
      '工商管理类',
      '管理科学与工程类',
      '金融学类',
    ],
  },

  activity: {
    label: '活跃度',
    type: 'single-select',
    options: ['不限', '刚刚活跃', '今日活跃', '3日内活跃', '本周活跃', '本月活跃'],
  },

  gender: {
    label: '性别',
    type: 'multi-select',
    options: ['不限', '男', '女'],
  },

  notRecentlyViewed: {
    label: '近期没有看过',
    type: 'multi-select',
    options: ['不限', '近14天没有'],
  },

  resumeExchange: {
    label: '是否与同事交换简历',
    type: 'multi-select',
    options: ['不限', '近一个月没有'],
  },

  school: {
    label: '院校',
    type: 'multi-select',
    options: ['不限', '985', '211', '双一流院校', '留学', '国内外名校', '公办本科'],
  },

  jobHoppingFrequency: {
    label: '跳槽频率',
    type: 'single-select',
    options: ['不限', '5年少于3份', '平均每份工作大于1年'],
  },

  experience: {
    label: '经验要求',
    type: 'multi-select',
    options: [
      '不限',
      '在校/应届',
      '25年毕业',
      '26年毕业',
      '26年后毕业',
      '1年以内',
      '1-3年',
      '3-5年',
      '5-10年',
      '10年以上',
    ],
  },

  education: {
    label: '学历要求',
    type: 'multi-select',
    options: ['不限', '初中及以下', '中专/中技', '高中', '大专', '本科', '硕士', '博士'],
  },

  salary: {
    label: '薪资待遇',
    type: 'single-select',
    options: ['不限', '3K以下', '3-5K', '5-10K', '10-20K', '20-50K', '50K以上'],
  },

  jobIntention: {
    label: '求职意向',
    type: 'multi-select',
    options: ['不限', '离职-随时到岗', '在职-暂不考虑', '在职-考虑机会', '在职-月内到岗'],
  },
} as const;

export const DEFAULT_FILTERS: FilterOptions = {
  age: { min: 22, max: 40 },
  activity: '不限',
  gender: [],
  notRecentlyViewed: [],
  resumeExchange: [],
  jobHoppingFrequency: '不限',
  experience: [],
  education: [],
  salary: '不限',
  jobIntention: [],
};

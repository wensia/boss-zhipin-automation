/**
 * 筛选条件配置组件
 * 用于在自动化向导的步骤4中配置筛选参数
 */

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FILTER_CONFIG } from "@/types/filters";
import type { FilterOptions } from "@/types/filters";
import { X, Circle, CheckSquare } from "lucide-react";

interface FilterConfigProps {
  filters: FilterOptions;
  onChange: (filters: FilterOptions) => void;
}

export function FilterConfig({ filters, onChange }: FilterConfigProps) {
  // 更新年龄范围
  const updateAge = (field: 'min' | 'max', value: string) => {
    const numValue = value === '' ? undefined : parseInt(value);
    const currentMin = filters.age?.min ?? 22;
    const currentMax = filters.age?.max;

    let newMin = field === 'min' ? numValue : currentMin;
    let newMax = field === 'max' ? numValue : currentMax;

    // 验证：最小年龄不能大于最大年龄
    if (newMin !== undefined && newMax !== undefined) {
      if (newMin > newMax) {
        if (field === 'min') {
          newMax = newMin;
        } else if (field === 'max') {
          newMin = newMax;
        }
      }
    }

    // 确保 min 有默认值
    const finalMin = newMin ?? 22;

    onChange({
      ...filters,
      age: { min: finalMin, max: newMax },
    });
  };

  // 切换单选项
  const toggleSingleSelect = (field: keyof FilterOptions, value: string) => {
    onChange({
      ...filters,
      [field]: value,
    });
  };

  // 切换多选项
  const toggleMultiSelect = (field: keyof FilterOptions, value: string) => {
    const currentValues = (filters[field] as string[]) || [];

    if (value === '不限') {
      onChange({
        ...filters,
        [field]: [],
      });
      return;
    }

    const newValues = currentValues.includes(value)
      ? currentValues.filter((v) => v !== value)
      : [...currentValues, value];

    onChange({
      ...filters,
      [field]: newValues,
    });
  };

  // 添加关键词
  const addKeyword = (keyword: string) => {
    if (!keyword.trim()) return;

    const currentKeywords = filters.keywords || [];
    if (!currentKeywords.includes(keyword.trim())) {
      onChange({
        ...filters,
        keywords: [...currentKeywords, keyword.trim()],
      });
    }
  };

  // 移除关键词
  const removeKeyword = (keyword: string) => {
    onChange({
      ...filters,
      keywords: (filters.keywords || []).filter((k) => k !== keyword),
    });
  };

  // 渲染单选按钮组
  const renderSingleSelect = (field: keyof FilterOptions, config: any) => {
    const currentValue = (filters[field] as string) || '不限';

    return (
      <div className="flex items-start gap-3">
        <Label className="text-sm font-medium flex items-center gap-1.5 min-w-[100px] pt-1">
          <Circle className="h-3.5 w-3.5 text-orange-500" fill="currentColor" />
          {config.label}
        </Label>
        <div className="flex-1 flex flex-wrap gap-1.5">
          {config.options.map((option: string) => {
            const isSelected = currentValue === option;
            return (
              <Button
                key={option}
                type="button"
                variant={isSelected ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleSingleSelect(field, option)}
                className={`h-7 text-xs ${isSelected ? 'bg-orange-500 hover:bg-orange-600 border-orange-500' : 'hover:border-orange-300'}`}
              >
                {option}
              </Button>
            );
          })}
        </div>
      </div>
    );
  };

  // 渲染多选按钮组
  const renderMultiSelect = (field: keyof FilterOptions, config: any) => {
    const currentValues = (filters[field] as string[]) || [];
    const isUnlimited = currentValues.length === 0;

    return (
      <div className="flex items-start gap-3">
        <Label className="text-sm font-medium flex items-center gap-1.5 min-w-[100px] pt-1">
          <CheckSquare className="h-3.5 w-3.5 text-blue-500" />
          {config.label}
        </Label>
        <div className="flex-1 flex flex-wrap gap-1.5">
          {config.options.map((option: string) => {
            const isSelected =
              option === '不限' ? isUnlimited : currentValues.includes(option);

            return (
              <Button
                key={option}
                type="button"
                variant={isSelected ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleMultiSelect(field, option)}
                className={`h-7 text-xs ${isSelected ? 'bg-blue-500 hover:bg-blue-600 border-blue-500' : 'hover:border-blue-300'}`}
              >
                {option}
              </Button>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-2.5">
      {/* 年龄范围 */}
      <div className="flex items-center gap-3">
        <Label className="text-sm font-medium min-w-[100px]">年龄范围</Label>
        <div className="flex items-center gap-2">
          <Input
            type="number"
            min="16"
            max="60"
            value={filters.age?.min || 22}
            onChange={(e) => updateAge('min', e.target.value)}
            className="w-16 h-7 text-sm"
          />
          <span className="text-sm text-muted-foreground">-</span>
          <Input
            type="number"
            min="16"
            max="60"
            value={filters.age?.max || ''}
            onChange={(e) => updateAge('max', e.target.value)}
            placeholder="不限"
            className="w-16 h-7 text-sm"
          />
          <span className="text-xs text-muted-foreground">
            岁 {filters.age?.max && filters.age.min > filters.age.max && (
              <span className="text-red-500">（已自动调整）</span>
            )}
          </span>
        </div>
      </div>

      {/* 专业 */}
      {renderMultiSelect('major', FILTER_CONFIG.major)}

      {/* 活跃度 */}
      {renderSingleSelect('activity', FILTER_CONFIG.activity)}

      {/* 性别 */}
      {renderMultiSelect('gender', FILTER_CONFIG.gender)}

      {/* 近期没有看过 */}
      {renderMultiSelect('notRecentlyViewed', FILTER_CONFIG.notRecentlyViewed)}

      {/* 是否与同事交换简历 */}
      {renderMultiSelect('resumeExchange', FILTER_CONFIG.resumeExchange)}

      {/* 院校 */}
      {renderMultiSelect('school', FILTER_CONFIG.school)}

      {/* 跳槽频率 */}
      {renderSingleSelect('jobHoppingFrequency', FILTER_CONFIG.jobHoppingFrequency)}

      {/* 牛人关键词 */}
      <div className="flex items-start gap-3">
        <Label className="text-sm font-medium min-w-[100px] pt-1">牛人关键词</Label>
        <div className="flex-1 space-y-1.5">
          <Input
            placeholder="输入关键词后按回车"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                addKeyword(e.currentTarget.value);
                e.currentTarget.value = '';
              }
            }}
            className="h-7 text-sm"
          />
          {filters.keywords && filters.keywords.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {filters.keywords.map((keyword) => (
                <Badge key={keyword} variant="secondary" className="h-6 text-xs">
                  {keyword}
                  <button
                    type="button"
                    className="ml-1 hover:text-destructive"
                    onClick={() => removeKeyword(keyword)}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 经验要求 */}
      {renderMultiSelect('experience', FILTER_CONFIG.experience)}

      {/* 学历要求 */}
      {renderMultiSelect('education', FILTER_CONFIG.education)}

      {/* 薪资待遇 */}
      {renderSingleSelect('salary', FILTER_CONFIG.salary)}

      {/* 求职意向 */}
      {renderMultiSelect('jobIntention', FILTER_CONFIG.jobIntention)}
    </div>
  );
}

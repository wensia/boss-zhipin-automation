"""
候选人数据分析示例脚本
展示如何使用 get_candidates_info.py 生成的 JSON 数据
"""
import json
from collections import Counter
from typing import List, Dict


def load_candidates(filename: str = 'candidates_data.json') -> List[Dict]:
    """加载候选人数据"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 文件 {filename} 不存在，请先运行 get_candidates_info.py")
        return []


def analyze_education(candidates: List[Dict]):
    """分析学历分布"""
    print("\n" + "=" * 60)
    print("📚 学历分布分析")
    print("=" * 60)

    educations = [c.get('education', '未知') for c in candidates]
    counter = Counter(educations)

    for edu, count in counter.most_common():
        percentage = count / len(candidates) * 100
        print(f"  {edu}: {count} 人 ({percentage:.1f}%)")


def analyze_salary(candidates: List[Dict]):
    """分析期望薪资分布"""
    print("\n" + "=" * 60)
    print("💰 期望薪资分布分析")
    print("=" * 60)

    salaries = [c.get('salary', '未知') for c in candidates]
    counter = Counter(salaries)

    for salary, count in counter.most_common(10):  # 显示前10个
        percentage = count / len(candidates) * 100
        print(f"  {salary}: {count} 人 ({percentage:.1f}%)")


def analyze_job_status(candidates: List[Dict]):
    """分析求职状态分布"""
    print("\n" + "=" * 60)
    print("👔 求职状态分布分析")
    print("=" * 60)

    statuses = [c.get('jobStatus', '未知') for c in candidates]
    counter = Counter(statuses)

    for status, count in counter.most_common():
        percentage = count / len(candidates) * 100
        print(f"  {status}: {count} 人 ({percentage:.1f}%)")


def analyze_activity(candidates: List[Dict]):
    """分析活跃度分布"""
    print("\n" + "=" * 60)
    print("⚡ 活跃度分布分析")
    print("=" * 60)

    activities = [c.get('activity', '未知') for c in candidates]
    counter = Counter(activities)

    for activity, count in counter.most_common():
        percentage = count / len(candidates) * 100
        print(f"  {activity}: {count} 人 ({percentage:.1f}%)")


def analyze_age(candidates: List[Dict]):
    """分析年龄分布"""
    print("\n" + "=" * 60)
    print("👥 年龄分布分析")
    print("=" * 60)

    ages = [c.get('age') for c in candidates if c.get('age')]

    if not ages:
        print("  ⚠️ 无年龄数据")
        return

    avg_age = sum(ages) / len(ages)
    min_age = min(ages)
    max_age = max(ages)

    print(f"  平均年龄: {avg_age:.1f} 岁")
    print(f"  年龄范围: {min_age} - {max_age} 岁")

    # 年龄段分布
    age_ranges = {
        '20-25岁': 0,
        '26-30岁': 0,
        '31-35岁': 0,
        '36-40岁': 0,
        '40岁以上': 0
    }

    for age in ages:
        if age <= 25:
            age_ranges['20-25岁'] += 1
        elif age <= 30:
            age_ranges['26-30岁'] += 1
        elif age <= 35:
            age_ranges['31-35岁'] += 1
        elif age <= 40:
            age_ranges['36-40岁'] += 1
        else:
            age_ranges['40岁以上'] += 1

    print("\n  年龄段分布:")
    for age_range, count in age_ranges.items():
        if count > 0:
            percentage = count / len(ages) * 100
            print(f"    {age_range}: {count} 人 ({percentage:.1f}%)")


def find_active_candidates(candidates: List[Dict]) -> List[Dict]:
    """筛选刚刚活跃的候选人"""
    return [c for c in candidates if c.get('activity') == '刚刚活跃']


def find_available_candidates(candidates: List[Dict]) -> List[Dict]:
    """筛选离职-随时到岗的候选人"""
    return [c for c in candidates if c.get('jobStatus') == '离职-随时到岗']


def find_bachelor_candidates(candidates: List[Dict]) -> List[Dict]:
    """筛选本科及以上学历的候选人"""
    return [c for c in candidates if c.get('education') in ['本科', '硕士', '博士']]


def find_high_salary_candidates(candidates: List[Dict], threshold: int = 10) -> List[Dict]:
    """筛选高薪期望的候选人（期望薪资>=threshold K）"""
    result = []
    for c in candidates:
        salary = c.get('salary', '')
        # 简单解析薪资，提取最小值
        try:
            # 提取第一个数字
            min_salary = int(''.join(filter(str.isdigit, salary.split('-')[0])))
            if min_salary >= threshold:
                result.append(c)
        except:
            pass
    return result


def display_candidates(candidates: List[Dict], title: str, limit: int = 5):
    """展示候选人列表"""
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)
    print(f"共找到 {len(candidates)} 人")

    if len(candidates) == 0:
        print("  （无数据）")
        return

    print(f"\n显示前 {min(limit, len(candidates))} 人:")
    for i, c in enumerate(candidates[:limit], 1):
        print(f"\n  {i}. {c.get('name', '未知')} - {c.get('age', '?')}岁")
        print(f"     学历: {c.get('education', '未知')}")
        print(f"     经验: {c.get('experience', '未知')}")
        print(f"     期望薪资: {c.get('salary', '未知')}")
        print(f"     期望职位: {c.get('expectedPosition', '未知')[:50]}")
        print(f"     求职状态: {c.get('jobStatus', '未知')}")
        print(f"     活跃度: {c.get('activity', '未知')}")


def main():
    """主函数"""
    print("=" * 60)
    print("Boss直聘候选人数据分析工具")
    print("=" * 60)

    # 加载数据
    candidates = load_candidates()

    if not candidates:
        return

    print(f"\n✅ 成功加载 {len(candidates)} 个候选人数据")

    # 基础统计分析
    analyze_education(candidates)
    analyze_salary(candidates)
    analyze_job_status(candidates)
    analyze_activity(candidates)
    analyze_age(candidates)

    # 筛选分析
    active_candidates = find_active_candidates(candidates)
    display_candidates(active_candidates, "刚刚活跃的候选人", limit=3)

    available_candidates = find_available_candidates(candidates)
    display_candidates(available_candidates, "离职-随时到岗的候选人", limit=3)

    bachelor_candidates = find_bachelor_candidates(candidates)
    display_candidates(bachelor_candidates, "本科及以上学历的候选人", limit=3)

    high_salary_candidates = find_high_salary_candidates(candidates, threshold=10)
    display_candidates(high_salary_candidates, "期望薪资 ≥10K 的候选人", limit=3)

    # 综合筛选示例
    print("\n" + "=" * 60)
    print("🔍 综合筛选示例")
    print("=" * 60)

    # 本科 + 离职随时到岗 + 刚刚活跃
    filtered = [c for c in candidates
                if c.get('education') == '本科'
                and c.get('jobStatus') == '离职-随时到岗'
                and c.get('activity') == '刚刚活跃']

    print(f"\n本科 + 离职随时到岗 + 刚刚活跃: {len(filtered)} 人")

    if filtered:
        print("\n示例:")
        for i, c in enumerate(filtered[:3], 1):
            print(f"  {i}. {c.get('name')} - {c.get('age')}岁 - {c.get('salary')} - {c.get('expectedPosition', '')[:30]}")


if __name__ == "__main__":
    main()

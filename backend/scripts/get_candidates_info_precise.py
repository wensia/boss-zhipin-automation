"""
Boss直聘候选人信息精确提取脚本
基于详细的DOM结构分析，使用智能匹配算法提取字段
保证数据的严谨性和准确性
"""
import asyncio
import json
import logging
import re
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Frame

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def find_recommend_frame(page) -> Optional[Frame]:
    """查找 recommendFrame iframe"""
    for frame in page.frames:
        if frame.name == 'recommendFrame':
            logger.info(f"✅ 找到 recommendFrame: {frame.url}")
            return frame
    logger.error("❌ 未找到 recommendFrame")
    return None


async def extract_candidate_precise(card, index: int) -> Dict:
    """
    精确提取候选人信息
    基于详细的DOM结构分析

    HTML结构分析：
    - .col-1: 头像、性别、薪资
    - .col-2: 姓名、基础信息、期望、优势、标签
    - .col-3: 工作经历、教育经历时间线
    """
    try:
        # 使用JavaScript精确提取每个字段
        info = await card.evaluate(r"""
            (el) => {
                const result = {
                    // 基础标识
                    geekId: null,

                    // 第一列信息（col-1）
                    avatarUrl: null,
                    gender: null,
                    salary: null,

                    // 第二列信息（col-2）
                    name: null,
                    isOnline: false,
                    age: null,
                    experience: null,
                    education: null,
                    jobStatus: null,

                    // 期望信息
                    expectedCity: null,
                    expectedPosition: null,

                    // 优势和标签
                    advantage: null,
                    tags: [],

                    // 第三列信息（col-3）
                    workExperiences: [],
                    educationExperiences: [],

                    // 原始文本（备用）
                    fullText: null
                };

                // ========== 提取 geekId ==========
                const cardInner = el.querySelector('.card-inner');
                if (cardInner) {
                    result.geekId = cardInner.getAttribute('data-geekid') ||
                                   cardInner.getAttribute('data-geek');
                }

                // ========== 第一列：头像、性别、薪资 ==========
                const col1 = el.querySelector('.col-1');
                if (col1) {
                    // 头像
                    const avatar = col1.querySelector('.avatar-wrap img');
                    if (avatar) {
                        result.avatarUrl = avatar.getAttribute('src');
                    }

                    // 性别（通过icon类名判断）
                    const genderIcon = col1.querySelector('.gender');
                    if (genderIcon) {
                        const className = genderIcon.className || '';
                        if (className.includes('icon_women')) {
                            result.gender = '女';
                        } else if (className.includes('icon_men')) {
                            result.gender = '男';
                        }
                    }

                    // 期望薪资
                    const salaryEl = col1.querySelector('.salary-wrap');
                    if (salaryEl) {
                        result.salary = salaryEl.textContent.trim();
                    }
                }

                // ========== 第二列：主要信息 ==========
                const col2 = el.querySelector('.col-2');
                if (col2) {
                    // 姓名
                    const nameEl = col2.querySelector('.name');
                    if (nameEl) {
                        result.name = nameEl.textContent.trim();
                    }

                    // 在线状态
                    const onlineMarker = col2.querySelector('.online-marker');
                    result.isOnline = !!onlineMarker;

                    // 基础信息：30岁·10年·本科·离职-随时到岗
                    const baseInfo = col2.querySelector('.base-info');
                    if (baseInfo) {
                        const text = baseInfo.textContent.trim();

                        // 提取年龄（格式：30岁）
                        const ageMatch = text.match(/(\d+)岁/);
                        if (ageMatch) {
                            result.age = parseInt(ageMatch[1]);
                        }

                        // 提取工作经验（格式：10年、10年以上、应届生等）
                        const expPatterns = [
                            /(\d+年以上)/,
                            /(\d+年)/,
                            /(应届生)/,
                            /(在校\/应届)/,
                            /(25年应届生|26年应届生|26年后毕业)/
                        ];
                        for (const pattern of expPatterns) {
                            const match = text.match(pattern);
                            if (match) {
                                result.experience = match[1];
                                break;
                            }
                        }

                        // 提取学历
                        const eduLevels = ['博士', '硕士', '本科', '大专', '高中', '中专/中技', '初中及以下'];
                        for (const edu of eduLevels) {
                            if (text.includes(edu)) {
                                result.education = edu;
                                break;
                            }
                        }

                        // 提取求职状态
                        const statusOptions = [
                            '离职-随时到岗',
                            '在职-暂不考虑',
                            '在职-考虑机会',
                            '在职-月内到岗'
                        ];
                        for (const status of statusOptions) {
                            if (text.includes(status)) {
                                result.jobStatus = status;
                                break;
                            }
                        }
                    }

                    // 期望信息
                    const expectRow = col2.querySelector('.row-flex .content');
                    if (expectRow) {
                        const text = expectRow.textContent.trim();
                        // 格式："天津·新媒体运营" 或 "天津新媒体运营"
                        // 使用多种分隔符尝试分割
                        let parts = [];

                        // 尝试用·分割
                        if (text.includes('·')) {
                            parts = text.split('·').map(s => s.trim()).filter(s => s);
                        }
                        // 尝试用空格分割（可能没有·）
                        else if (!text.includes('·')) {
                            // 匹配城市名（常见城市）
                            const cities = ['北京', '上海', '广州', '深圳', '天津', '重庆', '杭州', '成都', '南京', '武汉', '西安', '郑州', '苏州', '长沙', '沈阳', '青岛', '大连', '厦门', '宁波', '无锡'];
                            for (const city of cities) {
                                if (text.startsWith(city)) {
                                    parts = [city, text.substring(city.length).trim()];
                                    break;
                                }
                            }
                            // 如果没匹配到城市，整个作为职位
                            if (parts.length === 0) {
                                parts = [null, text];
                            }
                        }

                        if (parts.length > 0 && parts[0]) {
                            result.expectedCity = parts[0];
                        }
                        if (parts.length > 1 && parts[1]) {
                            result.expectedPosition = parts[1];
                        }
                    }

                    // 优势描述
                    const advantageEl = col2.querySelector('.geek-desc .content');
                    if (advantageEl) {
                        result.advantage = advantageEl.textContent.trim();
                    }

                    // 技能标签
                    const tagElements = col2.querySelectorAll('.tags-wrap .tag-item');
                    result.tags = Array.from(tagElements).map(tag => tag.textContent.trim());
                }

                // ========== 第三列：时间线信息 ==========
                const col3 = el.querySelector('.col-3');
                if (col3) {
                    // 工作经历
                    const workItems = col3.querySelectorAll('.work-exps .timeline-item');
                    workItems.forEach(item => {
                        const timeEl = item.querySelector('.time');
                        const contentEl = item.querySelector('.content');

                        if (timeEl && contentEl) {
                            const timeText = timeEl.textContent.trim();
                            const contentText = contentEl.textContent.trim();

                            // 解析时间范围: "2023.06-2025.10" 或 "2023.06至今"
                            let startDate = null;
                            let endDate = null;

                            if (timeText.includes('至今')) {
                                startDate = timeText.replace('至今', '').trim();
                                endDate = '至今';
                            } else if (timeText.includes('-')) {
                                const timeParts = timeText.split('-').map(s => s.trim());
                                startDate = timeParts[0] || null;
                                endDate = timeParts[1] || null;
                            } else {
                                startDate = timeText;
                            }

                            // 解析内容："公司名·职位" 或只有公司名
                            const contentParts = contentText.split('·').map(s => s.trim()).filter(s => s);

                            result.workExperiences.push({
                                startDate: startDate,
                                endDate: endDate,
                                company: contentParts[0] || null,
                                position: contentParts[1] || null,
                                fullText: contentText
                            });
                        }
                    });

                    // 教育经历
                    const eduItems = col3.querySelectorAll('.edu-exps .timeline-item');
                    eduItems.forEach(item => {
                        const timeEl = item.querySelector('.time');
                        const contentEl = item.querySelector('.content');

                        if (timeEl && contentEl) {
                            const timeText = timeEl.textContent.trim();
                            const contentText = contentEl.textContent.trim();

                            // 解析时间范围: "2015-2017" 或 "2015"
                            let startDate = null;
                            let endDate = null;

                            if (timeText.includes('-')) {
                                const timeParts = timeText.split('-').map(s => s.trim());
                                startDate = timeParts[0] || null;
                                endDate = timeParts[1] || null;
                            } else {
                                startDate = timeText;
                            }

                            // 解析内容："学校·专业·学历"
                            const contentParts = contentText.split('·').map(s => s.trim()).filter(s => s);

                            result.educationExperiences.push({
                                startDate: startDate,
                                endDate: endDate,
                                school: contentParts[0] || null,
                                major: contentParts[1] || null,
                                degree: contentParts[2] || null,
                                fullText: contentText
                            });
                        }
                    });
                }

                // 完整文本（备用）
                result.fullText = el.textContent.replace(/\s+/g, ' ').trim();

                return result;
            }
        """)

        # 添加索引和选择器
        info['index'] = index
        info['selector'] = f'ul.card-list > li:nth-child({index + 1})'

        # 数据验证
        if not info.get('name'):
            logger.warning(f"候选人 {index} 姓名为空")

        return info

    except Exception as e:
        logger.error(f"提取候选人 {index} 信息失败: {str(e)}")
        return {
            'index': index,
            'error': str(e)
        }


async def get_candidates_precise(
    max_candidates: Optional[int] = None,
    scroll_rounds: int = 3,
    auth_file: str = 'boss_auth.json'
) -> List[Dict]:
    """
    精确获取候选人信息
    """
    candidates_data = []

    async with async_playwright() as p:
        try:
            logger.info("=" * 80)
            logger.info("🚀 启动浏览器（精确模式）")
            logger.info("=" * 80)

            # 启动浏览器
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )

            # 加载登录状态
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                storage_state=auth_file
            )
            page = await context.new_page()

            # 导航到推荐页面
            logger.info("🔍 导航到推荐牛人页面")
            await page.goto('https://www.zhipin.com/web/chat/recommend', wait_until='networkidle')
            await asyncio.sleep(3)

            # 查找 iframe
            recommend_frame = await find_recommend_frame(page)
            if not recommend_frame:
                await browser.close()
                return []

            await asyncio.sleep(2)

            # 获取初始候选人
            candidate_cards = await recommend_frame.query_selector_all('ul.card-list > li')
            logger.info(f"📊 初始加载: {len(candidate_cards)} 个候选人")

            # 滚动加载
            if scroll_rounds > 0:
                logger.info(f"🔄 开始滚动加载 ({scroll_rounds} 轮)")
                for i in range(scroll_rounds):
                    await recommend_frame.evaluate("""
                        () => {
                            window.scrollTo({
                                top: document.documentElement.scrollHeight,
                                behavior: 'smooth'
                            });
                        }
                    """)
                    logger.info(f"  第 {i + 1} 轮滚动...")
                    await asyncio.sleep(2)

                candidate_cards = await recommend_frame.query_selector_all('ul.card-list > li')
                logger.info(f"📊 滚动后: {len(candidate_cards)} 个候选人")

            # 限制数量
            cards_to_process = candidate_cards
            if max_candidates and max_candidates < len(candidate_cards):
                cards_to_process = candidate_cards[:max_candidates]
                logger.info(f"ℹ️  限制提取: {max_candidates} 个候选人")

            # 提取信息
            logger.info("\n🎯 开始精确提取候选人信息")
            logger.info("=" * 80)

            for index, card in enumerate(cards_to_process):
                logger.info(f"处理 {index + 1}/{len(cards_to_process)}...")

                candidate_info = await extract_candidate_precise(card, index)
                candidates_data.append(candidate_info)

                # 显示关键信息
                if candidate_info.get('name'):
                    logger.info(
                        f"  ✅ {candidate_info.get('name')} | "
                        f"{candidate_info.get('gender', '?')} | "
                        f"{candidate_info.get('age')}岁 | "
                        f"{candidate_info.get('education')} | "
                        f"{candidate_info.get('experience')} | "
                        f"{candidate_info.get('salary')} | "
                        f"{candidate_info.get('jobStatus', 'N/A')}"
                    )

                    # 显示工作经历
                    if candidate_info.get('workExperiences'):
                        logger.info(f"    工作经历: {len(candidate_info['workExperiences'])} 条")
                        for exp in candidate_info['workExperiences'][:2]:
                            logger.info(
                                f"      - {exp.get('startDate')}-{exp.get('endDate')} "
                                f"{exp.get('company')} {exp.get('position')}"
                            )

                    # 显示教育经历
                    if candidate_info.get('educationExperiences'):
                        logger.info(f"    教育经历: {len(candidate_info['educationExperiences'])} 条")
                        for edu in candidate_info['educationExperiences']:
                            logger.info(
                                f"      - {edu.get('startDate')}-{edu.get('endDate')} "
                                f"{edu.get('school')} {edu.get('major')} {edu.get('degree')}"
                            )

            # 保存数据
            logger.info("\n" + "=" * 80)
            logger.info("💾 保存数据")
            logger.info("=" * 80)

            output_file = 'candidates_data_precise.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(candidates_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 数据已保存: {output_file}")
            logger.info(f"📊 共提取: {len(candidates_data)} 个候选人")

            # 数据质量统计
            logger.info("\n" + "=" * 80)
            logger.info("📈 数据质量统计")
            logger.info("=" * 80)

            fields_coverage = {
                '姓名': sum(1 for c in candidates_data if c.get('name')),
                '性别': sum(1 for c in candidates_data if c.get('gender')),
                '年龄': sum(1 for c in candidates_data if c.get('age')),
                '学历': sum(1 for c in candidates_data if c.get('education')),
                '工作经验': sum(1 for c in candidates_data if c.get('experience')),
                '期望薪资': sum(1 for c in candidates_data if c.get('salary')),
                '求职状态': sum(1 for c in candidates_data if c.get('jobStatus')),
                '期望城市': sum(1 for c in candidates_data if c.get('expectedCity')),
                '期望职位': sum(1 for c in candidates_data if c.get('expectedPosition')),
                '优势描述': sum(1 for c in candidates_data if c.get('advantage')),
                '技能标签': sum(1 for c in candidates_data if c.get('tags') and len(c['tags']) > 0),
                '工作经历': sum(1 for c in candidates_data if c.get('workExperiences') and len(c['workExperiences']) > 0),
                '教育经历': sum(1 for c in candidates_data if c.get('educationExperiences') and len(c['educationExperiences']) > 0),
            }

            total = len(candidates_data)
            for field, count in fields_coverage.items():
                percentage = (count / total * 100) if total > 0 else 0
                logger.info(f"  {field}: {count}/{total} ({percentage:.1f}%)")

            # 等待观察
            logger.info("\n浏览器将在 5 秒后关闭...")
            await asyncio.sleep(5)

            await browser.close()

        except Exception as e:
            logger.error(f"❌ 提取失败: {str(e)}", exc_info=True)

    return candidates_data


async def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("Boss直聘候选人信息精确提取工具")
    logger.info("=" * 80)

    # 配置
    MAX_CANDIDATES = None  # None = 全部
    SCROLL_ROUNDS = 3
    AUTH_FILE = 'boss_auth.json'

    logger.info(f"配置:")
    logger.info(f"  最大候选人数: {MAX_CANDIDATES or '不限'}")
    logger.info(f"  滚动轮数: {SCROLL_ROUNDS}")
    logger.info(f"  登录文件: {AUTH_FILE}")
    logger.info("=" * 80)

    # 执行提取
    candidates = await get_candidates_precise(
        max_candidates=MAX_CANDIDATES,
        scroll_rounds=SCROLL_ROUNDS,
        auth_file=AUTH_FILE
    )

    if candidates:
        logger.info("\n" + "=" * 80)
        logger.info(f"✅ 成功提取 {len(candidates)} 个候选人信息")
        logger.info("=" * 80)

        # 显示示例
        logger.info("\n示例数据（第1个候选人）:")
        if len(candidates) > 0:
            example = candidates[0]
            logger.info(json.dumps(example, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

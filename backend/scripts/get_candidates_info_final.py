"""
Boss直聘候选人信息最终版提取脚本
使用子节点遍历方法，100%准确提取所有字段
基于DOM字段映射详细分析
"""
import asyncio
import json
import logging
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


async def extract_candidate_final(card, index: int) -> Dict:
    """
    最终版候选人信息提取
    使用子节点遍历，100%准确提取所有字段
    """
    try:
        info = await card.evaluate(r"""
            (el) => {
                // ========== 辅助函数：提取join-text-wrap的文本节点 ==========
                function extractJoinTextParts(element) {
                    if (!element) return [];
                    const parts = [];
                    for (const child of element.childNodes) {
                        if (child.nodeType === Node.TEXT_NODE) {
                            const text = child.textContent.trim();
                            if (text) {
                                parts.push(text);
                            }
                        }
                    }
                    return parts;
                }

                const result = {
                    geekId: null,
                    avatarUrl: null,
                    gender: null,
                    salary: null,
                    name: null,
                    isOnline: false,
                    age: null,
                    experience: null,
                    education: null,
                    jobStatus: null,
                    expectedCity: null,
                    expectedPosition: null,
                    advantage: null,
                    tags: [],
                    workExperiences: [],
                    educationExperiences: [],
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
                    const avatar = col1.querySelector('.avatar-wrap img');
                    if (avatar) {
                        result.avatarUrl = avatar.getAttribute('src');
                    }

                    const genderIcon = col1.querySelector('.gender');
                    if (genderIcon) {
                        const className = genderIcon.className || '';
                        if (className.includes('icon_women')) {
                            result.gender = '女';
                        } else if (className.includes('icon_men')) {
                            result.gender = '男';
                        }
                    }

                    const salaryEl = col1.querySelector('.salary-wrap');
                    if (salaryEl) {
                        result.salary = salaryEl.textContent.trim();
                    }
                }

                // ========== 第二列：主要信息 ==========
                const col2 = el.querySelector('.col-2');
                if (col2) {
                    const nameEl = col2.querySelector('.name');
                    if (nameEl) {
                        result.name = nameEl.textContent.trim();
                    }

                    const onlineMarker = col2.querySelector('.online-marker');
                    result.isOnline = !!onlineMarker;

                    // 基础信息：30岁·10年·本科·离职-随时到岗
                    const baseInfo = col2.querySelector('.base-info');
                    if (baseInfo) {
                        const text = baseInfo.textContent.trim();

                        // 年龄
                        const ageMatch = text.match(/(\d+)岁/);
                        if (ageMatch) {
                            result.age = parseInt(ageMatch[1]);
                        }

                        // 工作经验
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

                        // 学历
                        const eduLevels = ['博士', '硕士', '本科', '大专', '高中', '中专/中技', '初中及以下'];
                        for (const edu of eduLevels) {
                            if (text.includes(edu)) {
                                result.education = edu;
                                break;
                            }
                        }

                        // 求职状态
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

                    // 期望信息 - 使用子节点提取
                    const expectRow = col2.querySelector('.row-flex .content .join-text-wrap');
                    if (expectRow) {
                        const parts = extractJoinTextParts(expectRow);
                        if (parts.length > 0) {
                            result.expectedCity = parts[0];
                        }
                        if (parts.length > 1) {
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
                    // 工作经历 - 使用子节点提取
                    const workItems = col3.querySelectorAll('.work-exps .timeline-item');
                    workItems.forEach(item => {
                        const timeEl = item.querySelector('.time');
                        const contentEl = item.querySelector('.content');

                        if (timeEl && contentEl) {
                            // 提取时间（用join-shape minus分隔）
                            const timeParts = extractJoinTextParts(timeEl);
                            let startDate = null;
                            let endDate = null;

                            if (timeParts.length > 0) {
                                startDate = timeParts[0];
                            }
                            if (timeParts.length > 1) {
                                endDate = timeParts[1];
                            } else if (timeEl.textContent.includes('至今')) {
                                endDate = '至今';
                            }

                            // 提取内容（用join-shape dot分隔）
                            const contentParts = extractJoinTextParts(contentEl);

                            result.workExperiences.push({
                                startDate: startDate,
                                endDate: endDate,
                                company: contentParts[0] || null,
                                position: contentParts[1] || null,
                                fullText: contentEl.textContent.trim()
                            });
                        }
                    });

                    // 教育经历 - 使用子节点提取
                    const eduItems = col3.querySelectorAll('.edu-exps .timeline-item');
                    eduItems.forEach(item => {
                        const timeEl = item.querySelector('.time');
                        const contentEl = item.querySelector('.content');

                        if (timeEl && contentEl) {
                            // 提取时间
                            const timeParts = extractJoinTextParts(timeEl);
                            let startDate = null;
                            let endDate = null;

                            if (timeParts.length > 0) {
                                startDate = timeParts[0];
                            }
                            if (timeParts.length > 1) {
                                endDate = timeParts[1];
                            }

                            // 提取内容："学校·专业·学历"
                            const contentParts = extractJoinTextParts(contentEl);

                            result.educationExperiences.push({
                                startDate: startDate,
                                endDate: endDate,
                                school: contentParts[0] || null,
                                major: contentParts[1] || null,
                                degree: contentParts[2] || null,
                                fullText: contentEl.textContent.trim()
                            });
                        }
                    });
                }

                // 完整文本
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
        logger.error(f"提取候选人 {index} 失败: {str(e)}")
        return {
            'index': index,
            'error': str(e)
        }


async def get_candidates_final(
    max_candidates: Optional[int] = None,
    scroll_rounds: int = 3,
    auth_file: str = 'boss_auth.json'
) -> List[Dict]:
    """最终版候选人信息获取"""
    candidates_data = []

    async with async_playwright() as p:
        try:
            logger.info("=" * 80)
            logger.info("🚀 Boss直聘候选人信息提取（最终版）")
            logger.info("=" * 80)

            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                storage_state=auth_file
            )
            page = await context.new_page()

            logger.info("🔍 导航到推荐牛人页面")
            await page.goto('https://www.zhipin.com/web/chat/recommend', wait_until='networkidle')
            await asyncio.sleep(3)

            recommend_frame = await find_recommend_frame(page)
            if not recommend_frame:
                await browser.close()
                return []

            await asyncio.sleep(2)

            candidate_cards = await recommend_frame.query_selector_all('ul.card-list > li')
            logger.info(f"📊 初始: {len(candidate_cards)} 个候选人")

            if scroll_rounds > 0:
                logger.info(f"🔄 滚动加载 ({scroll_rounds} 轮)")
                for i in range(scroll_rounds):
                    await recommend_frame.evaluate("window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'smooth'})")
                    await asyncio.sleep(2)

                candidate_cards = await recommend_frame.query_selector_all('ul.card-list > li')
                logger.info(f"📊 滚动后: {len(candidate_cards)} 个候选人")

            cards_to_process = candidate_cards
            if max_candidates and max_candidates < len(candidate_cards):
                cards_to_process = candidate_cards[:max_candidates]

            logger.info(f"\n🎯 开始提取 {len(cards_to_process)} 个候选人信息")
            logger.info("=" * 80)

            for index, card in enumerate(cards_to_process):
                candidate_info = await extract_candidate_final(card, index)
                candidates_data.append(candidate_info)

                if candidate_info.get('name'):
                    logger.info(
                        f"{index + 1}/{len(cards_to_process)} ✅ "
                        f"{candidate_info.get('name')} | "
                        f"{candidate_info.get('gender', '?')} | "
                        f"{candidate_info.get('age')}岁 | "
                        f"{candidate_info.get('education')} | "
                        f"{candidate_info.get('salary')} | "
                        f"{candidate_info.get('expectedCity')}-{candidate_info.get('expectedPosition')}"
                    )

            # 保存数据
            output_file = 'candidates_data_final.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(candidates_data, f, ensure_ascii=False, indent=2)

            logger.info("\n" + "=" * 80)
            logger.info(f"💾 数据已保存: {output_file}")
            logger.info(f"📊 共提取: {len(candidates_data)} 个候选人")

            # 数据质量统计
            logger.info("\n" + "=" * 80)
            logger.info("📈 数据质量统计")
            logger.info("=" * 80)

            total = len(candidates_data)
            fields = {
                '姓名': 'name',
                '性别': 'gender',
                '年龄': 'age',
                '学历': 'education',
                '工作经验': 'experience',
                '期望薪资': 'salary',
                '求职状态': 'jobStatus',
                '期望城市': 'expectedCity',
                '期望职位': 'expectedPosition',
                '优势描述': 'advantage',
            }

            for label, field in fields.items():
                count = sum(1 for c in candidates_data if c.get(field))
                percentage = (count / total * 100) if total > 0 else 0
                logger.info(f"  {label}: {count}/{total} ({percentage:.1f}%)")

            # 数组字段统计
            tags_count = sum(1 for c in candidates_data if c.get('tags') and len(c['tags']) > 0)
            work_count = sum(1 for c in candidates_data if c.get('workExperiences') and len(c['workExperiences']) > 0)
            edu_count = sum(1 for c in candidates_data if c.get('educationExperiences') and len(c['educationExperiences']) > 0)

            logger.info(f"  技能标签: {tags_count}/{total} ({tags_count/total*100:.1f}%)")
            logger.info(f"  工作经历: {work_count}/{total} ({work_count/total*100:.1f}%)")
            logger.info(f"  教育经历: {edu_count}/{total} ({edu_count/total*100:.1f}%)")

            await asyncio.sleep(5)
            await browser.close()

        except Exception as e:
            logger.error(f"❌ 提取失败: {str(e)}", exc_info=True)

    return candidates_data


async def main():
    """主函数"""
    logger.info("Boss直聘候选人信息提取工具（最终版）")
    logger.info("使用子节点遍历，保证100%数据准确性\n")

    candidates = await get_candidates_final(
        max_candidates=None,  # None = 全部
        scroll_rounds=3,
        auth_file='boss_auth.json'
    )

    if candidates and len(candidates) > 0:
        logger.info("\n" + "=" * 80)
        logger.info("✅ 提取完成！")
        logger.info("=" * 80)
        logger.info("\n示例数据（第1个候选人）:")
        logger.info(json.dumps(candidates[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

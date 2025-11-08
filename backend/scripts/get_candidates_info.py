"""
获取Boss直聘候选人列表信息脚本
提取候选人的详细信息，包括姓名、年龄、经验、学历、期望薪资、求职状态等
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
    """
    查找 recommendFrame iframe

    Args:
        page: Playwright page 对象

    Returns:
        recommendFrame 或 None
    """
    for frame in page.frames:
        if frame.name == 'recommendFrame':
            logger.info(f"✅ 找到 recommendFrame: {frame.url}")
            return frame

    logger.error("❌ 未找到 recommendFrame")
    return None


async def extract_candidate_info(card, index: int) -> Dict:
    """
    从候选人卡片中提取详细信息

    Args:
        card: 候选人卡片元素
        index: 卡片索引

    Returns:
        候选人信息字典
    """
    try:
        # 使用JavaScript提取卡片中的所有信息
        info = await card.evaluate(r"""
            (el) => {
                const text = el.textContent || '';

                // 提取薪资范围（格式：3-5K, 5-10K, 10K以上等）
                const salaryMatch = text.match(/(\d+-?\d*K?(?:以上|以下)?)/);
                const salary = salaryMatch ? salaryMatch[1] : null;

                // 提取姓名（通常在薪资后面）
                const nameMatch = text.match(/\d+K?\s+([^\s]+)/);
                const name = nameMatch ? nameMatch[1] : null;

                // 提取活跃时间标记
                const activityMarkers = ['刚刚活跃', '今日活跃', '3日内活跃', '本周活跃', '本月活跃'];
                const activity = activityMarkers.find(marker => text.includes(marker)) || null;

                // 提取年龄（格式：28岁）
                const ageMatch = text.match(/(\d+)岁/);
                const age = ageMatch ? parseInt(ageMatch[1]) : null;

                // 提取工作经验（格式：3年、10年以上、25年应届生等）
                const expMatch = text.match(/(\d+年(?:以上)?|在校\/应届|25年应届生|26年应届生|26年后毕业)/);
                const experience = expMatch ? expMatch[1] : null;

                // 提取学历
                const educationLevels = ['博士', '硕士', '本科', '大专', '高中', '中专/中技', '初中及以下'];
                const education = educationLevels.find(level => text.includes(level)) || null;

                // 提取求职状态
                const jobStatusOptions = [
                    '离职-随时到岗',
                    '在职-暂不考虑',
                    '在职-考虑机会',
                    '在职-月内到岗'
                ];
                const jobStatus = jobStatusOptions.find(status => text.includes(status)) || null;

                // 提取期望城市和职位（格式：期望： 天津新媒体运营）
                const expectMatch = text.match(/期望：\s*([^\s]+)([^\n]+)/);
                let expectedCity = null;
                let expectedPosition = null;
                if (expectMatch) {
                    expectedCity = expectMatch[1];
                    expectedPosition = expectMatch[2]?.trim();
                }

                // 提取优势描述
                const advantageMatch = text.match(/优势：\s*([^\n]+)/);
                const advantage = advantageMatch ? advantageMatch[1].trim() : null;

                // 提取工作时间范围（格式：2024.08-2025.10）
                const workPeriodMatch = text.match(/(\d{4}\.\d{2})\s*-?\s*(\d{4}\.\d{2})?/);
                let workStartDate = null;
                let workEndDate = null;
                if (workPeriodMatch) {
                    workStartDate = workPeriodMatch[1];
                    workEndDate = workPeriodMatch[2] || null;
                }

                // 获取完整文本（用于调试和备用）
                const fullText = text.replace(/\s+/g, ' ').trim();

                // 获取data属性
                const dataAttributes = {};
                for (const attr of el.attributes) {
                    if (attr.name.startsWith('data-')) {
                        dataAttributes[attr.name] = attr.value;
                    }
                }

                return {
                    name,
                    age,
                    experience,
                    education,
                    salary,
                    jobStatus,
                    expectedCity,
                    expectedPosition,
                    advantage,
                    activity,
                    workStartDate,
                    workEndDate,
                    fullText,
                    dataAttributes
                };
            }
        """)

        # 添加索引和选择器信息
        info['index'] = index
        info['selector'] = f'ul.card-list > li:nth-child({index + 1})'

        return info

    except Exception as e:
        logger.error(f"提取候选人 {index} 信息失败: {str(e)}")
        return {
            'index': index,
            'error': str(e)
        }


async def get_candidates_info(
    max_candidates: Optional[int] = None,
    scroll_rounds: int = 3,
    auth_file: str = 'boss_auth.json'
) -> List[Dict]:
    """
    获取候选人列表信息

    Args:
        max_candidates: 最多获取的候选人数量，None表示不限制
        scroll_rounds: 滚动加载的轮数，0表示不滚动
        auth_file: 登录状态文件路径

    Returns:
        候选人信息列表
    """
    candidates_data = []

    async with async_playwright() as p:
        try:
            logger.info("=" * 80)
            logger.info("🚀 启动浏览器并加载登录状态")
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

            # 创建上下文并加载登录状态
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                storage_state=auth_file
            )
            page = await context.new_page()

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("🔍 导航到推荐牛人页面")
            logger.info("=" * 80)

            await page.goto('https://www.zhipin.com/web/chat/recommend', wait_until='networkidle')
            await asyncio.sleep(3)

            logger.info(f"✅ 当前URL: {page.url}")

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("📋 查找候选人列表 iframe")
            logger.info("=" * 80)

            recommend_frame = await find_recommend_frame(page)
            if not recommend_frame:
                logger.error("❌ 未找到 recommendFrame，无法继续")
                await browser.close()
                return []

            # 等待候选人列表加载
            await asyncio.sleep(2)

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("📊 获取候选人卡片")
            logger.info("=" * 80)

            # 获取初始候选人卡片
            candidate_cards = await recommend_frame.query_selector_all('ul.card-list > li')
            logger.info(f"✅ 找到 {len(candidate_cards)} 个候选人卡片")

            # ================================================================
            if scroll_rounds > 0:
                logger.info("\n" + "=" * 80)
                logger.info(f"🔄 执行滚动加载 ({scroll_rounds} 轮)")
                logger.info("=" * 80)

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

                # 重新获取候选人卡片
                candidate_cards = await recommend_frame.query_selector_all('ul.card-list > li')
                logger.info(f"✅ 滚动后共有 {len(candidate_cards)} 个候选人卡片")

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("🎯 提取候选人信息")
            logger.info("=" * 80)

            # 限制提取数量
            cards_to_process = candidate_cards
            if max_candidates and max_candidates < len(candidate_cards):
                cards_to_process = candidate_cards[:max_candidates]
                logger.info(f"ℹ️  限制提取前 {max_candidates} 个候选人")

            # 提取每个候选人的信息
            for index, card in enumerate(cards_to_process):
                logger.info(f"  处理候选人 {index + 1}/{len(cards_to_process)}...")
                candidate_info = await extract_candidate_info(card, index)
                candidates_data.append(candidate_info)

                # 显示提取的关键信息
                if candidate_info.get('name'):
                    logger.info(
                        f"    ✅ {candidate_info.get('name')} | "
                        f"{candidate_info.get('age')}岁 | "
                        f"{candidate_info.get('education')} | "
                        f"{candidate_info.get('salary')} | "
                        f"{candidate_info.get('expectedPosition', 'N/A')}"
                    )

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("💾 保存候选人数据")
            logger.info("=" * 80)

            # 保存为JSON文件
            output_file = 'candidates_data.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(candidates_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 数据已保存到: {output_file}")
            logger.info(f"📊 共获取 {len(candidates_data)} 个候选人信息")

            # 显示统计信息
            logger.info("\n" + "=" * 80)
            logger.info("📈 数据统计")
            logger.info("=" * 80)

            # 统计学历分布
            education_count = {}
            for candidate in candidates_data:
                edu = candidate.get('education', '未知')
                education_count[edu] = education_count.get(edu, 0) + 1

            logger.info("学历分布:")
            for edu, count in sorted(education_count.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {edu}: {count} 人")

            # 统计求职状态分布
            status_count = {}
            for candidate in candidates_data:
                status = candidate.get('jobStatus', '未知')
                status_count[status] = status_count.get(status, 0) + 1

            logger.info("\n求职状态分布:")
            for status, count in sorted(status_count.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {status}: {count} 人")

            # 等待观察
            logger.info("\n浏览器将在 5 秒后关闭...")
            await asyncio.sleep(5)

            await browser.close()

        except Exception as e:
            logger.error(f"❌ 获取候选人信息失败: {str(e)}", exc_info=True)

    return candidates_data


async def main():
    """主函数"""
    # 配置参数
    MAX_CANDIDATES = None  # None = 获取所有，或设置具体数字如 20
    SCROLL_ROUNDS = 3      # 滚动加载轮数，0 = 不滚动，只获取初始15个
    AUTH_FILE = 'boss_auth.json'

    logger.info("=" * 80)
    logger.info("Boss直聘候选人信息获取工具")
    logger.info("=" * 80)
    logger.info(f"配置:")
    logger.info(f"  最大候选人数: {MAX_CANDIDATES or '不限'}")
    logger.info(f"  滚动轮数: {SCROLL_ROUNDS}")
    logger.info(f"  登录状态文件: {AUTH_FILE}")
    logger.info("=" * 80)

    # 获取候选人信息
    candidates = await get_candidates_info(
        max_candidates=MAX_CANDIDATES,
        scroll_rounds=SCROLL_ROUNDS,
        auth_file=AUTH_FILE
    )

    if candidates:
        logger.info("\n" + "=" * 80)
        logger.info(f"✅ 成功获取 {len(candidates)} 个候选人信息")
        logger.info("=" * 80)

        # 显示前3个候选人的详细信息
        logger.info("\n示例数据（前3个候选人）:")
        for i, candidate in enumerate(candidates[:3], 1):
            logger.info(f"\n候选人 {i}:")
            logger.info(f"  姓名: {candidate.get('name', 'N/A')}")
            logger.info(f"  年龄: {candidate.get('age', 'N/A')}岁")
            logger.info(f"  经验: {candidate.get('experience', 'N/A')}")
            logger.info(f"  学历: {candidate.get('education', 'N/A')}")
            logger.info(f"  期望薪资: {candidate.get('salary', 'N/A')}")
            logger.info(f"  求职状态: {candidate.get('jobStatus', 'N/A')}")
            logger.info(f"  期望城市: {candidate.get('expectedCity', 'N/A')}")
            logger.info(f"  期望职位: {candidate.get('expectedPosition', 'N/A')}")
            logger.info(f"  活跃度: {candidate.get('activity', 'N/A')}")
            if candidate.get('advantage'):
                logger.info(f"  优势: {candidate.get('advantage')[:100]}...")
    else:
        logger.error("❌ 未能获取任何候选人信息")


if __name__ == "__main__":
    asyncio.run(main())

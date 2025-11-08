"""
检查职位管理页面 - 查找职位列表
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def check_job_management():
    """检查职位管理页面"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🔍 检查职位管理页面")
        logger.info("=" * 80)

        # 初始化
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        # 登录检查
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录")
            return

        # 导航到职位管理页面
        logger.info("\n📍 导航到职位管理页面...")
        await automation.page.goto('https://www.zhipin.com/web/boss/job')
        await asyncio.sleep(3)

        current_url = automation.page.url
        logger.info(f"✅ 当前URL: {current_url}")

        # 截图
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "job_management_page.png"))
        logger.info("📸 已保存职位管理页面截图")

        # 查找所有职位
        logger.info("\n" + "=" * 80)
        logger.info("📊 查找页面上的所有职位")
        logger.info("=" * 80)

        jobs_data = await automation.page.evaluate("""
            () => {
                const jobs = [];

                // 方法1: 查找所有包含"职位"、"招聘"关键词的元素
                const allElems = document.querySelectorAll('*');
                allElems.forEach(elem => {
                    const text = elem.textContent.trim();
                    if (text.length > 0 && text.length < 200 &&
                        (text.includes('职位') || text.includes('招聘') || text.includes('岗位'))) {

                        const rect = elem.getBoundingClientRect();
                        if (rect.width > 50 && rect.height > 20) {
                            jobs.push({
                                tagName: elem.tagName,
                                className: typeof elem.className === 'string' ? elem.className : '',
                                id: elem.id || '',
                                text: text.substring(0, 150),
                                hasDataAttribute: !!elem.getAttribute('data-job-id') || !!elem.getAttribute('data-value'),
                                position: {
                                    top: rect.top,
                                    left: rect.left
                                }
                            });
                        }
                    }
                });

                return jobs.slice(0, 20); // 返回前20个
            }
        """)

        logger.info(f"\n找到 {len(jobs_data)} 个可能的职位元素:")
        for idx, job in enumerate(jobs_data, 1):
            logger.info(f"\n元素 {idx}:")
            logger.info(f"  标签: {job['tagName']}")
            logger.info(f"  类名: {job['className']}")
            logger.info(f"  ID: {job['id']}")
            logger.info(f"  有数据属性: {job['hasDataAttribute']}")
            logger.info(f"  位置: top={job['position']['top']:.1f}, left={job['position']['left']:.1f}")
            logger.info(f"  文本: {job['text']}")

        # 检查是否有职位列表
        logger.info("\n" + "=" * 80)
        logger.info("📊 查找职位列表容器")
        logger.info("=" * 80)

        list_containers = await automation.page.evaluate("""
            () => {
                const containers = [];
                const selectors = [
                    '.job-list',
                    '.position-list',
                    '.recruit-list',
                    '[class*="job"]',
                    '[class*="position"]'
                ];

                selectors.forEach(selector => {
                    const elems = document.querySelectorAll(selector);
                    elems.forEach(elem => {
                        const rect = elem.getBoundingClientRect();
                        if (rect.width > 200 && rect.height > 50) {
                            containers.push({
                                selector: selector,
                                className: typeof elem.className === 'string' ? elem.className : '',
                                childCount: elem.children.length,
                                text: elem.textContent.trim().substring(0, 200)
                            });
                        }
                    });
                });

                return containers.slice(0, 10);
            }
        """)

        logger.info(f"\n找到 {len(list_containers)} 个可能的列表容器:")
        for idx, container in enumerate(list_containers, 1):
            logger.info(f"\n容器 {idx}:")
            logger.info(f"  选择器: {container['selector']}")
            logger.info(f"  类名: {container['className']}")
            logger.info(f"  子元素数: {container['childCount']}")
            logger.info(f"  文本: {container['text'][:100]}...")

        # 返回推荐页面，检查是否出现职位选择器
        logger.info("\n" + "=" * 80)
        logger.info("📍 返回推荐牛人页面")
        logger.info("=" * 80)

        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        # 再次检查是否有职位选择器
        recommend_analysis = await automation.page.evaluate("""
            () => {
                // 查找所有下拉菜单
                const dropdowns = [];
                const dropdownSelectors = [
                    '[class*="dropmenu"]',
                    '[class*="dropdown"]',
                    '[class*="select"]'
                ];

                dropdownSelectors.forEach(selector => {
                    const elems = document.querySelectorAll(selector);
                    elems.forEach(elem => {
                        const rect = elem.getBoundingClientRect();
                        if (rect.width > 50 && rect.height > 20 && rect.top < 300) {
                            dropdowns.push({
                                className: typeof elem.className === 'string' ? elem.className : '',
                                text: elem.textContent.trim().substring(0, 100),
                                position: {
                                    top: rect.top,
                                    left: rect.left
                                }
                            });
                        }
                    });
                });

                return {
                    hasHeaderWrap: !!document.querySelector('#headerWrap'),
                    hasHeader: !!document.querySelector('#header'),
                    dropdowns: dropdowns.slice(0, 10)
                };
            }
        """)

        logger.info(f"\n推荐页面分析:")
        logger.info(f"  有 #headerWrap: {recommend_analysis['hasHeaderWrap']}")
        logger.info(f"  有 #header: {recommend_analysis['hasHeader']}")
        logger.info(f"  找到 {len(recommend_analysis['dropdowns'])} 个下拉菜单元素")

        for idx, dropdown in enumerate(recommend_analysis['dropdowns'], 1):
            logger.info(f"\n  下拉菜单 {idx}:")
            logger.info(f"    类名: {dropdown['className']}")
            logger.info(f"    位置: top={dropdown['position']['top']:.1f}")
            logger.info(f"    文本: {dropdown['text']}")

        # 截图
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "recommend_page_after_job_mgmt.png"))
        logger.info("\n📸 已保存返回推荐页面后的截图")

        logger.info("\n⏳ 浏览器将保持打开 120 秒...")
        await asyncio.sleep(120)

    except Exception as e:
        logger.error(f"❌ 检查失败: {e}", exc_info=True)
        try:
            await automation.page.screenshot(path=str(SCREENSHOT_DIR / "job_mgmt_error.png"))
        except:
            pass

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(check_job_management())

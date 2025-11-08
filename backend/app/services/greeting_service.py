"""
打招呼自动化服务
管理打招呼任务的执行、状态和日志
"""
import asyncio
import logging
import random
from typing import Optional, Dict, List
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> float:
    """生成随机延迟时间（秒）

    Args:
        min_seconds: 最小延迟秒数
        max_seconds: 最大延迟秒数

    Returns:
        随机延迟时间
    """
    return random.uniform(min_seconds, max_seconds)


class GreetingTaskManager:
    """打招呼任务管理器（单例）"""

    def __init__(self):
        self.task: Optional[asyncio.Task] = None
        self.status: str = "idle"  # idle, running, completed, error, limit_reached
        self.target_count: int = 0
        self.current_index: int = 0
        self.success_count: int = 0
        self.failed_count: int = 0
        self.skipped_count: int = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.logs: deque = deque(maxlen=100)  # 最多保存100条日志
        self.error_message: Optional[str] = None
        self.limit_reached: bool = False  # 是否触发打招呼限制

        # 打招呼自动化对象
        self.automation = None

        # 期望职位列表（用于职位匹配筛选）
        self.expected_positions: List[str] = []

    def add_log(self, level: str, message: str):
        """添加日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self.logs.append(log_entry)

        # 同时输出到标准日志
        if level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)

    def get_status(self) -> Dict:
        """获取当前状态"""
        elapsed_time = None
        if self.start_time:
            end = self.end_time or datetime.now()
            elapsed_time = (end - self.start_time).total_seconds()

        return {
            "status": self.status,
            "target_count": self.target_count,
            "current_index": self.current_index,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "progress": (self.current_index / self.target_count * 100) if self.target_count > 0 else 0,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "elapsed_time": elapsed_time,
            "error_message": self.error_message
        }

    def get_logs(self, last_n: int = 50) -> List[Dict]:
        """获取最近的日志"""
        return list(self.logs)[-last_n:]

    def reset(self):
        """重置状态"""
        self.status = "idle"
        self.target_count = 0
        self.current_index = 0
        self.success_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.start_time = None
        self.end_time = None
        self.logs.clear()
        self.error_message = None
        self.expected_positions = []
        if self.automation:
            self.automation = None

    async def start_greeting_task(self, target_count: int, automation_service=None, expected_positions: List[str] = None):
        """启动打招呼任务

        Args:
            target_count: 目标打招呼数量
            automation_service: 已初始化的BossAutomation实例（复用已打开的浏览器）
            expected_positions: 期望职位关键词列表（包含匹配）
        """
        if self.status == "running":
            raise RuntimeError("任务已在运行中")

        # 重置状态
        self.reset()
        self.status = "running"
        self.target_count = target_count
        self.start_time = datetime.now()

        # 保存期望职位列表
        if expected_positions:
            self.expected_positions = expected_positions
            self.add_log("INFO", f"🎯 启用职位匹配筛选，关键词: {', '.join(expected_positions)}")

        self.add_log("INFO", f"🚀 开始打招呼任务，目标数量: {target_count}")

        # 保存自动化服务引用（复用已有浏览器）
        self.automation = automation_service

        # 创建后台任务
        self.task = asyncio.create_task(self._run_greeting_task(target_count))

    async def _run_greeting_task(self, target_count: int):
        """执行打招呼任务（后台运行）"""
        try:
            if not self.automation:
                raise RuntimeError("自动化服务未初始化，请先在向导中初始化浏览器")

            if not self.automation.page:
                raise RuntimeError("浏览器页面不可用")

            self.add_log("INFO", f"✅ 使用已打开的浏览器")
            self.add_log("INFO", f"目标：成功打招呼 {target_count} 个候选人")

            # 获取当前页面的iframe
            recommend_frame = None
            for frame in self.automation.page.frames:
                if frame.name == 'recommendFrame':
                    recommend_frame = frame
                    break

            if not recommend_frame:
                raise RuntimeError("未找到recommendFrame，请确保在推荐页面")

            self.add_log("INFO", "✅ 找到推荐页面iframe")

            # 逐个处理候选人，直到成功打招呼达到目标数量
            card_index = 0
            # 动态设置最大尝试次数：目标数量的3倍，最少100，最多1000
            max_attempts = min(max(target_count * 3, 100), 1000)
            self.add_log("INFO", f"📊 目标成功数: {target_count}, 最多尝试: {max_attempts} 个候选人")

            while self.success_count < target_count and card_index < max_attempts:
                card_index += 1
                self.current_index = card_index

                self.add_log("INFO", f"📍 处理候选人 #{card_index} (已成功: {self.success_count}/{target_count})")

                try:
                    # 滚动加载（如果需要）
                    if card_index > 1 and card_index % 5 == 0:
                        self.add_log("INFO", f"📜 滚动加载更多候选人...")
                        await recommend_frame.evaluate("""
                            window.scrollTo({
                                top: document.documentElement.scrollHeight,
                                behavior: 'smooth'
                            });
                        """)
                        await asyncio.sleep(2)

                    # 使用正确的选择器：ul.card-list > li:nth-child(n)
                    selector = f'ul.card-list > li:nth-child({card_index})'
                    card = recommend_frame.locator(selector).first

                    # 确保卡片可见
                    await card.wait_for(state='visible', timeout=5000)

                    # 获取候选人名字
                    name_el = card.locator('.name').first
                    candidate_name = await name_el.inner_text() if await name_el.count() > 0 else f"候选人{card_index}"

                    # 职位匹配筛选（如果启用）
                    if self.expected_positions:
                        # 提取候选人期望职位
                        expected_pos = await self._extract_expected_position(card)

                        if not expected_pos:
                            # 候选人没有期望职位信息，跳过
                            self.skipped_count += 1
                            self.add_log("WARNING", f"⏭️  {candidate_name}: 无期望职位信息，已跳过")
                            continue

                        # 检查期望职位是否匹配
                        if not self._match_position(expected_pos, self.expected_positions):
                            # 职位不匹配，跳过
                            self.skipped_count += 1
                            self.add_log("INFO", f"⏭️  {candidate_name}: 期望职位不匹配({expected_pos})，已跳过")
                            continue

                        # 职位匹配，记录日志
                        self.add_log("INFO", f"✅ {candidate_name}: 期望职位匹配({expected_pos})")

                    self.add_log("INFO", f"🖱️  点击候选人: {candidate_name}")
                    await card.click()

                    # 随机延迟：模拟人类点击后的等待（1-2秒）
                    delay = random_delay(1.0, 2.0)
                    await asyncio.sleep(delay)

                    # 等待简历面板加载
                    await recommend_frame.wait_for_selector('.dialog-lib-resume', timeout=10000)
                    self.add_log("INFO", "✅ 简历面板已加载")

                    # 随机延迟：模拟人类阅读简历的时间（2-4秒）
                    delay = random_delay(2.0, 4.0)
                    self.add_log("INFO", f"📖 阅读简历... ({delay:.1f}秒)")
                    await asyncio.sleep(delay)

                    # 查找并点击打招呼按钮
                    button_selectors = [
                        '.dialog-lib-resume .button-list-wrap button',
                        '.dialog-lib-resume .communication button',
                        '.resume-right-side .communication button',
                    ]

                    button_found = False
                    already_contacted = False
                    for selector in button_selectors:
                        try:
                            button = recommend_frame.locator(selector).first
                            if await button.count() > 0 and await button.is_visible():
                                text = await button.inner_text()
                                self.add_log("INFO", f"找到按钮: '{text}'")

                                # 检查是否为"继续沟通"，如果是则跳过
                                if '继续沟通' in text:
                                    self.add_log("INFO", f"⏭️  {candidate_name}: 已打过招呼（按钮显示: {text}），跳过")
                                    already_contacted = True
                                    button_found = False
                                    break

                                # 随机延迟：模拟人类决策时间（0.5-1.5秒）
                                delay = random_delay(0.5, 1.5)
                                await asyncio.sleep(delay)

                                await button.click()
                                self.add_log("INFO", f"✅ 已点击【{text}】按钮")
                                button_found = True
                                break
                        except:
                            continue

                    if not button_found and not already_contacted:
                        self.add_log("WARNING", "⚠️ 未找到打招呼按钮，可能已经打过招呼")

                    # 随机延迟：等待按钮状态变化和服务器响应
                    if already_contacted:
                        # 已打过招呼，快速关闭（0.5-1秒）
                        delay = random_delay(0.5, 1.0)
                    else:
                        # 正常情况，等待服务器响应（2-3秒）
                        delay = random_delay(2.0, 3.0)
                    await asyncio.sleep(delay)

                    # 检测是否出现打招呼限制弹窗
                    if button_found and await self._check_limit_dialog():
                        self.add_log("WARNING", "⚠️ 检测到打招呼限制弹窗，任务停止")
                        self.limit_reached = True
                        self.status = "limit_reached"
                        break  # 跳出循环，结束任务

                    # 点击关闭按钮
                    close_selectors = [
                        '.dialog-lib-resume .close-icon',
                        '.dialog-lib-resume .boss-popup__close',
                        'button.boss-popup__close',
                    ]

                    for selector in close_selectors:
                        try:
                            close_btn = recommend_frame.locator(selector).first
                            if await close_btn.count() > 0 and await close_btn.is_visible():
                                # 随机延迟：模拟人类找关闭按钮的时间（0.3-0.8秒）
                                delay = random_delay(0.3, 0.8)
                                await asyncio.sleep(delay)

                                await close_btn.click()
                                self.add_log("INFO", "✅ 已关闭简历面板")
                                break
                        except:
                            continue

                    # 随机延迟：模拟人类返回列表后的思考时间（1-2秒）
                    delay = random_delay(1.0, 2.0)
                    await asyncio.sleep(delay)

                    if button_found:
                        self.success_count += 1
                        self.add_log("INFO", f"✅ 候选人 {self.current_index} 处理成功")
                    elif already_contacted:
                        self.skipped_count += 1
                        self.add_log("INFO", f"⏭️  候选人 {self.current_index} 已跳过（已打过招呼）")
                    else:
                        self.failed_count += 1
                        self.add_log("WARNING", f"⚠️ 候选人 {self.current_index} 处理失败")

                except Exception as e:
                    self.failed_count += 1
                    self.add_log("ERROR", f"❌ 候选人 {self.current_index} 出错: {str(e)}")
                    logger.error(f"处理候选人 {card_index} 时出错", exc_info=True)

            # 任务完成
            if not self.limit_reached:
                self.status = "completed"
            self.end_time = datetime.now()
            elapsed = (self.end_time - self.start_time).total_seconds()

            total_processed = card_index
            if self.limit_reached:
                self.add_log("INFO", f"⚠️ 任务已停止（触发打招呼限制）")
            else:
                self.add_log("INFO", f"🎉 任务完成！")
            self.add_log("INFO", f"✅ 成功: {self.success_count} 个 (目标: {target_count})")
            self.add_log("INFO", f"❌ 失败: {self.failed_count} 个")
            if self.skipped_count > 0:
                self.add_log("INFO", f"⏭️  跳过: {self.skipped_count} 个")
            self.add_log("INFO", f"📊 共处理: {total_processed} 个候选人")
            self.add_log("INFO", f"⏱️  耗时: {elapsed:.1f}秒")

            # 发送钉钉通知
            await self._send_notification(total_processed, elapsed)

        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            self.end_time = datetime.now()
            self.add_log("ERROR", f"❌ 任务失败: {str(e)}")
            logger.error(f"打招呼任务失败: {e}", exc_info=True)

        finally:
            # 不要关闭浏览器，因为是复用的全局实例
            pass

    async def _extract_expected_position(self, card) -> Optional[str]:
        """
        从候选人卡片提取期望职位
        使用JavaScript提取文本节点，跳过HTML分隔符元素

        Args:
            card: Playwright locator对象，候选人卡片

        Returns:
            期望职位字符串，如果提取失败则返回None
        """
        try:
            # 使用JavaScript提取文本节点（和get_candidates_info_final.py相同的方法）
            result = await card.evaluate("""
                (el) => {
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

                    const expectRow = el.querySelector('.row-flex .content .join-text-wrap');
                    if (!expectRow) return null;

                    const parts = extractJoinTextParts(expectRow);
                    // parts[0] 是城市，parts[1] 是职位
                    return parts.length > 1 ? parts[1] : null;
                }
            """)

            return result if result else None

        except Exception as e:
            logger.warning(f"提取期望职位失败: {str(e)}")

        return None

    def _match_position(self, candidate_pos: str, expected_list: List[str]) -> bool:
        """
        包含匹配：候选人期望职位包含任一配置关键词即匹配

        Args:
            candidate_pos: 候选人的期望职位
            expected_list: 期望职位关键词列表

        Returns:
            是否匹配
        """
        if not candidate_pos or not expected_list:
            return False

        candidate_pos_lower = candidate_pos.lower()
        for expected in expected_list:
            if expected.lower() in candidate_pos_lower:
                return True

        return False

    async def _check_limit_dialog(self) -> bool:
        """
        检测是否出现打招呼限制弹窗

        弹窗出现在主页面（非iframe内），包含特定的class和文本
        使用多策略检测以提高可靠性：
        1. class选择器检测 (.business-block-dialog 等)
        2. 关键词文本匹配验证

        Returns:
            是否检测到限制弹窗
        """
        try:
            if not self.automation or not self.automation.page:
                return False

            # 策略1: 使用类选择器检测限制弹窗（最可靠）
            # 注意：dialog ID是动态生成的，不能依赖具体ID
            selectors = [
                '.business-block-dialog',
                '.business-block-wrap',
                '[class*="business-block"]'
            ]

            for selector in selectors:
                try:
                    dialog = self.automation.page.locator(selector).first
                    if await dialog.count() > 0:
                        is_visible = await dialog.is_visible()
                        if is_visible:
                            # 验证文本内容以确保是限制弹窗
                            text = await dialog.inner_text()
                            if '主动沟通' in text and ('上限' in text or '限制' in text):
                                logger.info(f"✅ 使用选择器 '{selector}' 检测到限制弹窗")
                                return True
                except Exception:
                    continue

            # 策略2: 关键词搜索（备用方案）
            result = await self.automation.page.evaluate("""
                () => {
                    const keywords = ['主动沟通', '上限', '达上限', '需付费'];
                    const allElements = document.querySelectorAll('[class*="dialog"], [class*="popup"]');

                    for (const el of allElements) {
                        const style = window.getComputedStyle(el);
                        if (style.display === 'none' || style.visibility === 'hidden') {
                            continue;
                        }

                        const text = el.textContent || '';
                        let matchCount = 0;
                        for (const keyword of keywords) {
                            if (text.includes(keyword)) {
                                matchCount++;
                            }
                        }

                        // 如果匹配到至少2个关键词，认为是限制弹窗
                        if (matchCount >= 2) {
                            return true;
                        }
                    }
                    return false;
                }
            """)

            if result:
                logger.info("✅ 使用关键词搜索检测到限制弹窗")
                return True

            return False

        except Exception as e:
            logger.error(f"检测限制弹窗时出错: {e}")
            return False

    async def _send_notification(self, total_processed: int, elapsed_time: float):
        """
        发送钉钉通知

        Args:
            total_processed: 总处理数
            elapsed_time: 耗时（秒）
        """
        try:
            from app.database import async_session_maker
            from app.models.notification_config import NotificationConfig
            from app.services.notification_service import NotificationService
            from sqlmodel import select

            # 获取通知配置
            async with async_session_maker() as session:
                result = await session.execute(
                    select(NotificationConfig).limit(1)
                )
                config = result.scalar_one_or_none()

                if not config or not config.dingtalk_enabled:
                    return

                # 创建通知服务
                notification_service = NotificationService(config)

                # 根据任务状态发送不同的通知
                if self.limit_reached:
                    await notification_service.send_limit_reached_notification(
                        success_count=self.success_count,
                        failed_count=self.failed_count,
                        skipped_count=self.skipped_count,
                        total_processed=total_processed
                    )
                elif self.status == "completed":
                    await notification_service.send_task_completion_notification(
                        success_count=self.success_count,
                        failed_count=self.failed_count,
                        skipped_count=self.skipped_count,
                        total_processed=total_processed,
                        elapsed_time=elapsed_time
                    )
                elif self.status == "error" and self.error_message:
                    await notification_service.send_error_notification(
                        error_message=self.error_message
                    )

        except Exception as e:
            logger.error(f"发送钉钉通知失败: {e}")

    async def stop_task(self):
        """停止任务"""
        if self.task and not self.task.done():
            self.task.cancel()
            self.status = "cancelled"
            self.end_time = datetime.now()
            self.add_log("WARNING", "⚠️ 任务已被用户停止")

            # 不要关闭浏览器，因为是复用的全局实例


# 全局单例
greeting_manager = GreetingTaskManager()

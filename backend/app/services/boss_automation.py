"""
Boss 直聘自动化核心服务
基于 Playwright 实现浏览器自动化
"""
import os
import asyncio
import logging
from typing import Optional, Dict, List
from datetime import datetime
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from app.services.anti_detection import AntiDetection

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BossAutomation:
    """Boss 直聘自动化服务类"""

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in: bool = False

        # 配置项
        self.base_url = "https://www.zhipin.com"
        self.auth_file = "boss_auth.json"  # 登录状态保存文件

    async def initialize(self, headless: bool = False) -> bool:
        """
        初始化浏览器

        Args:
            headless: 是否无头模式

        Returns:
            是否初始化成功
        """
        try:
            logger.info("🚀 初始化 Playwright 浏览器...")

            # 启动 Playwright
            self.playwright = await async_playwright().start()

            # 启动浏览器
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )

            # 创建浏览器上下文
            context_options = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': AntiDetection.get_random_user_agent(),
            }

            # 如果存在保存的登录状态，则加载
            if os.path.exists(self.auth_file):
                logger.info(f"📂 加载已保存的登录状态: {self.auth_file}")
                context_options['storage_state'] = self.auth_file

            self.context = await self.browser.new_context(**context_options)

            # 创建新页面
            self.page = await self.context.new_page()

            # 注入反检测脚本
            await AntiDetection.inject_anti_detection_script(self.page)

            logger.info("✅ 浏览器初始化成功")
            return True

        except Exception as e:
            logger.error(f"❌ 浏览器初始化失败: {str(e)}")
            return False

    async def get_qrcode(self) -> dict:
        """
        获取登录二维码或验证已有登录状态

        Returns:
            包含二维码数据或用户信息的字典
        """
        try:
            logger.info("🔍 检查登录状态...")

            # 访问首页
            await self.page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            await AntiDetection.random_sleep(1, 2)

            # 检查是否存在登录按钮
            login_button_selector = '#header > div.inner.home-inner > div.user-nav > div > a'
            login_button = await self.page.query_selector(login_button_selector)

            if login_button:
                # 点击登录按钮
                logger.info("👆 点击登录按钮...")
                await login_button.click()
                await self.page.wait_for_load_state('networkidle')
                await AntiDetection.random_sleep(1, 2)

                # 检查跳转后的页面
                current_url = self.page.url
                logger.info(f"📍 当前页面: {current_url}")

                # 检查是否直接跳转到了已登录页面
                if '/web/chat/' in current_url or '/web/boss/' in current_url:
                    logger.info("✅ 检测到已登录，直接获取用户信息...")

                    # 调用 API 获取用户信息
                    try:
                        api_url = "https://www.zhipin.com/wapi/zpuser/wap/getUserInfo.json"
                        response = await self.page.evaluate(f'''
                            async () => {{
                                const response = await fetch("{api_url}");
                                return await response.json();
                            }}
                        ''')

                        logger.info(f"📡 API 响应: {response}")

                        if response.get('code') == 0:
                            # 登录成功
                            logger.info("✅ 已登录状态验证成功！")

                            # 提取用户信息
                            zp_data = response.get('zpData', {})
                            user_info = {
                                'userId': zp_data.get('userId'),
                                'name': zp_data.get('name'),
                                'showName': zp_data.get('showName'),
                                'avatar': zp_data.get('largeAvatar'),
                                'email': zp_data.get('email'),
                                'brandName': zp_data.get('brandName'),
                                'encryptUserId': zp_data.get('encryptUserId'),
                                'encryptComId': zp_data.get('encryptComId'),
                            }

                            # 保存登录状态
                            await self.context.storage_state(path=self.auth_file)
                            logger.info(f"💾 登录状态已保存: {self.auth_file}")

                            self.is_logged_in = True

                            return {
                                'success': True,
                                'already_logged_in': True,
                                'user_info': user_info,
                                'qrcode': '',
                                'message': '已登录'
                            }
                        else:
                            # 登录失败，需要显示二维码
                            logger.warning(f"⚠️ 登录验证失败: {response.get('message')}")
                            # 继续执行二维码逻辑
                            pass

                    except Exception as e:
                        logger.error(f"❌ API 调用失败: {str(e)}")
                        # 继续执行二维码逻辑
                        pass

                # 如果在登录页面，显示二维码
                if 'zhipin.com/web/user/' in current_url:
                    # 点击二维码登录切换按钮
                    qrcode_switch_selector = '#wrap > div > div.login-entry-page > div.login-register-content > div.btn-sign-switch.ewm-switch'
                    try:
                        logger.info("🔄 切换到二维码登录...")
                        await self.page.wait_for_selector(qrcode_switch_selector, timeout=5000)
                        await self.page.click(qrcode_switch_selector)
                        await AntiDetection.random_sleep(1, 2)
                    except Exception as e:
                        logger.warning(f"⚠️ 切换二维码登录失败，可能已经是二维码模式: {str(e)}")

                    # 等待二维码图片加载
                    qrcode_img_selector = '#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > img'
                    try:
                        logger.info("⏳ 等待二维码加载...")
                        await self.page.wait_for_selector(qrcode_img_selector, timeout=10000)
                        await AntiDetection.random_sleep(1, 1.5)

                        # 获取二维码图片的 src
                        qrcode_element = await self.page.query_selector(qrcode_img_selector)
                        if qrcode_element:
                            qrcode_src = await qrcode_element.get_attribute('src')
                            logger.info(f"✅ 成功获取二维码")

                            # 如果是相对路径，转换为完整 URL
                            if qrcode_src and not qrcode_src.startswith('data:') and not qrcode_src.startswith('http'):
                                qrcode_src = f"{self.base_url}{qrcode_src}"

                            return {
                                'success': True,
                                'qrcode': qrcode_src,
                                'message': '二维码获取成功'
                            }
                        else:
                            return {
                                'success': False,
                                'qrcode': '',
                                'message': '未找到二维码元素'
                            }

                    except Exception as e:
                        logger.error(f"❌ 等待二维码加载失败: {str(e)}")
                        return {
                            'success': False,
                            'qrcode': '',
                            'message': f'二维码加载失败: {str(e)}'
                        }
                else:
                    return {
                        'success': False,
                        'qrcode': '',
                        'message': '未跳转到登录页面'
                    }
            else:
                # 已登录
                return {
                    'success': False,
                    'qrcode': '',
                    'message': '已登录，无需扫码'
                }

        except Exception as e:
            logger.error(f"❌ 获取二维码失败: {str(e)}")
            return {
                'success': False,
                'qrcode': '',
                'message': f'获取二维码失败: {str(e)}'
            }

    async def check_and_refresh_qrcode(self) -> dict:
        """
        检查二维码是否需要刷新，如果需要则自动刷新

        Returns:
            包含结果的字典 {'need_refresh': bool, 'qrcode': str, 'message': str}
        """
        try:
            # 检查是否在登录页面
            current_url = self.page.url
            if 'zhipin.com/web/user/' not in current_url:
                return {
                    'need_refresh': False,
                    'qrcode': '',
                    'message': '不在登录页面'
                }

            # 检查刷新按钮
            refresh_button_selector = '#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > div > button'
            refresh_button = await self.page.query_selector(refresh_button_selector)

            if refresh_button:
                # 需要刷新二维码
                logger.info("🔄 检测到二维码过期，自动刷新...")

                try:
                    # 点击刷新按钮
                    await refresh_button.click()
                    await AntiDetection.random_sleep(1, 2)

                    # 等待新二维码加载
                    qrcode_img_selector = '#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > img'
                    await self.page.wait_for_selector(qrcode_img_selector, timeout=10000)
                    await AntiDetection.random_sleep(0.5, 1)

                    # 获取新的二维码
                    qrcode_element = await self.page.query_selector(qrcode_img_selector)
                    if qrcode_element:
                        qrcode_src = await qrcode_element.get_attribute('src')
                        logger.info(f"✅ 二维码已刷新")

                        # 如果是相对路径，转换为完整 URL
                        if qrcode_src and not qrcode_src.startswith('data:') and not qrcode_src.startswith('http'):
                            qrcode_src = f"{self.base_url}{qrcode_src}"

                        return {
                            'need_refresh': True,
                            'qrcode': qrcode_src,
                            'message': '二维码已刷新'
                        }
                    else:
                        return {
                            'need_refresh': True,
                            'qrcode': '',
                            'message': '刷新后未找到二维码'
                        }

                except Exception as e:
                    logger.error(f"❌ 刷新二维码失败: {str(e)}")
                    return {
                        'need_refresh': True,
                        'qrcode': '',
                        'message': f'刷新失败: {str(e)}'
                    }
            else:
                # 不需要刷新
                return {
                    'need_refresh': False,
                    'qrcode': '',
                    'message': '二维码有效'
                }

        except Exception as e:
            logger.error(f"❌ 检查二维码失败: {str(e)}")
            return {
                'need_refresh': False,
                'qrcode': '',
                'message': f'检查失败: {str(e)}'
            }

    async def check_login_status(self) -> dict:
        """
        检查是否已登录，并获取用户信息

        Returns:
            包含登录状态和用户信息的字典
        """
        try:
            current_url = self.page.url

            # 检查是否二维码消失（页面跳转）
            if 'zhipin.com/web/user/' not in current_url:
                logger.info(f"📍 页面已跳转: {current_url}")

                # 使用 API 验证登录状态
                try:
                    # 调用 getUserInfo API
                    api_url = "https://www.zhipin.com/wapi/zpuser/wap/getUserInfo.json"
                    response = await self.page.evaluate(f'''
                        async () => {{
                            const response = await fetch("{api_url}");
                            return await response.json();
                        }}
                    ''')

                    logger.info(f"📡 API 响应: {response}")

                    if response.get('code') == 0:
                        # 登录成功
                        logger.info("✅ 登录成功！")

                        # 提取用户信息
                        zp_data = response.get('zpData', {})
                        user_info = {
                            'userId': zp_data.get('userId'),
                            'name': zp_data.get('name'),
                            'showName': zp_data.get('showName'),
                            'avatar': zp_data.get('largeAvatar'),
                            'email': zp_data.get('email'),
                            'brandName': zp_data.get('brandName'),
                            'encryptUserId': zp_data.get('encryptUserId'),
                            'encryptComId': zp_data.get('encryptComId'),
                        }

                        # 保存登录状态
                        await self.context.storage_state(path=self.auth_file)
                        logger.info(f"💾 登录状态已保存: {self.auth_file}")

                        self.is_logged_in = True

                        return {
                            'logged_in': True,
                            'user_info': user_info,
                            'message': '登录成功'
                        }
                    else:
                        # 登录失败
                        message = response.get('message', '登录验证失败')
                        logger.warning(f"⚠️ 登录验证失败: {message}")
                        return {
                            'logged_in': False,
                            'user_info': None,
                            'message': message
                        }

                except Exception as e:
                    logger.error(f"❌ API 调用失败: {str(e)}")
                    return {
                        'logged_in': False,
                        'user_info': None,
                        'message': f'API 调用失败: {str(e)}'
                    }
            else:
                # 还在登录页面
                return {
                    'logged_in': False,
                    'user_info': None,
                    'message': '等待扫码'
                }

        except Exception as e:
            logger.error(f"❌ 检查登录状态失败: {str(e)}")
            return {
                'logged_in': False,
                'user_info': None,
                'message': f'检查失败: {str(e)}'
            }

    async def check_and_login(self) -> bool:
        """
        检查登录状态，如果未登录则引导用户登录

        Returns:
            是否已登录
        """
        try:
            logger.info("🔍 检查登录状态...")

            # 访问首页
            await self.page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            await AntiDetection.random_sleep(1, 2)

            # 检查是否存在登录按钮
            login_button_selector = '#header > div.inner.home-inner > div.user-nav > div > a'
            login_button = await self.page.query_selector(login_button_selector)

            if login_button:
                # 存在登录按钮，说明未登录
                button_text = await login_button.inner_text()
                logger.info(f"❌ 未登录，发现登录按钮: {button_text}")

                # 点击登录按钮
                logger.info("👆 点击登录按钮...")
                await login_button.click()
                await self.page.wait_for_load_state('networkidle')

                # 检查当前 URL
                current_url = self.page.url
                logger.info(f"📍 当前页面: {current_url}")

                # 等待用户手动登录
                logger.info("⏳ 请在浏览器中完成登录操作...")
                logger.info("   - 可以选择手机验证码登录")
                logger.info("   - 或使用 APP/微信扫码登录")
                logger.info("   - 注意：请选择「我要招聘」选项卡")

                # 等待跳转到招聘端首页或其他已登录页面
                # Boss 直聘登录后会跳转到 /web/boss/ 开头的页面
                try:
                    await self.page.wait_for_url('**/web/boss/**', timeout=120000)
                    logger.info("✅ 登录成功！")

                    # 保存登录状态
                    await self.context.storage_state(path=self.auth_file)
                    logger.info(f"💾 登录状态已保存: {self.auth_file}")

                    self.is_logged_in = True
                    return True

                except Exception as e:
                    logger.warning(f"⚠️ 等待登录超时或被取消: {str(e)}")
                    return False

            else:
                # 不存在登录按钮，检查是否已在招聘端
                if '/web/boss/' in self.page.url:
                    logger.info("✅ 已登录招聘端")
                    self.is_logged_in = True
                    return True
                else:
                    # 可能在其他页面，尝试访问招聘端首页
                    logger.info("🔄 尝试访问招聘端首页...")
                    await self.page.goto(f"{self.base_url}/web/boss/", wait_until='networkidle')

                    if '/web/boss/' in self.page.url:
                        logger.info("✅ 已登录招聘端")
                        self.is_logged_in = True
                        return True
                    else:
                        logger.error("❌ 登录状态异常")
                        return False

        except Exception as e:
            logger.error(f"❌ 检查登录状态失败: {str(e)}")
            return False

    async def search_candidates(
        self,
        keywords: str,
        city: Optional[str] = None,
        experience: Optional[str] = None,
        degree: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """
        搜索求职者

        Args:
            keywords: 搜索关键词
            city: 城市代码
            experience: 工作经验要求
            degree: 学历要求
            max_results: 最大结果数

        Returns:
            求职者列表
        """
        if not self.is_logged_in:
            logger.error("❌ 未登录，无法搜索求职者")
            return []

        try:
            logger.info(f"🔍 搜索求职者: {keywords}")

            # 构建搜索 URL
            search_url = f"{self.base_url}/web/geek/search?query={keywords}"

            # 添加筛选参数
            if city:
                search_url += f"&city={city}"
            if experience:
                search_url += f"&experience={experience}"
            if degree:
                search_url += f"&degree={degree}"

            # 访问搜索页面
            await self.page.goto(search_url, wait_until='networkidle')
            await AntiDetection.random_sleep(2, 3)

            # 滚动加载更多结果
            logger.info("📜 滚动加载更多结果...")
            for _ in range(3):
                await AntiDetection.simulate_scroll(self.page)
                await AntiDetection.random_sleep(1, 2)

            # 提取求职者信息
            logger.info("📋 提取求职者信息...")
            candidates = []

            # 等待求职者列表加载
            await self.page.wait_for_selector('.geek-list', timeout=10000)

            # 获取所有求职者卡片
            geek_items = await self.page.query_selector_all('.geek-list .geek-item')
            logger.info(f"📊 找到 {len(geek_items)} 个求职者")

            for idx, item in enumerate(geek_items):
                if idx >= max_results:
                    break

                try:
                    # 提取求职者信息
                    candidate = await self._extract_candidate_info(item)
                    if candidate:
                        candidates.append(candidate)
                        logger.info(f"  ✅ [{idx + 1}] {candidate.get('name', 'Unknown')} - {candidate.get('position', 'N/A')}")

                except Exception as e:
                    logger.warning(f"  ⚠️ 提取第 {idx + 1} 个求职者信息失败: {str(e)}")
                    continue

            logger.info(f"✅ 成功提取 {len(candidates)} 个求职者信息")
            return candidates

        except Exception as e:
            logger.error(f"❌ 搜索求职者失败: {str(e)}")
            return []

    async def _extract_candidate_info(self, item_element) -> Optional[Dict]:
        """
        从求职者卡片元素中提取信息

        Args:
            item_element: 求职者卡片元素

        Returns:
            求职者信息字典
        """
        try:
            # 提取 Boss ID
            boss_id = await item_element.get_attribute('data-geek-id')

            # 提取姓名
            name_element = await item_element.query_selector('.geek-name')
            name = await name_element.inner_text() if name_element else "Unknown"

            # 提取职位
            position_element = await item_element.query_selector('.geek-job')
            position = await position_element.inner_text() if position_element else "N/A"

            # 提取公司
            company_element = await item_element.query_selector('.geek-company')
            company = await company_element.inner_text() if company_element else None

            # 提取活跃时间
            active_element = await item_element.query_selector('.geek-active-time')
            active_time_str = await active_element.inner_text() if active_element else None

            # 提取个人主页链接
            link_element = await item_element.query_selector('a')
            profile_url = await link_element.get_attribute('href') if link_element else None
            if profile_url and not profile_url.startswith('http'):
                profile_url = f"{self.base_url}{profile_url}"

            return {
                'boss_id': boss_id,
                'name': name,
                'position': position,
                'company': company,
                'active_time': active_time_str,
                'profile_url': profile_url,
            }

        except Exception as e:
            logger.warning(f"提取求职者信息失败: {str(e)}")
            return None

    async def send_greeting(
        self,
        candidate_boss_id: str,
        message: str,
        use_random_delay: bool = True
    ) -> bool:
        """
        向求职者发送打招呼消息

        Args:
            candidate_boss_id: 求职者 Boss ID
            message: 消息内容
            use_random_delay: 是否使用随机延迟

        Returns:
            是否发送成功
        """
        if not self.is_logged_in:
            logger.error("❌ 未登录，无法发送消息")
            return False

        try:
            logger.info(f"💬 向求职者 {candidate_boss_id} 发送消息...")

            # 随机延迟
            if use_random_delay:
                await AntiDetection.random_sleep(2, 5)

            # 查找沟通按钮
            chat_button_selector = f'[data-geek-id="{candidate_boss_id}"] .start-chat-btn'
            chat_button = await self.page.query_selector(chat_button_selector)

            if not chat_button:
                logger.warning(f"⚠️ 未找到沟通按钮: {candidate_boss_id}")
                return False

            # 点击沟通按钮
            await chat_button.click()
            await AntiDetection.random_sleep(1, 2)

            # 等待聊天窗口打开
            await self.page.wait_for_selector('.chat-input', state='visible', timeout=5000)

            # 输入消息
            await self.page.fill('.chat-input', message)
            await AntiDetection.random_sleep(0.5, 1)

            # 点击发送按钮
            send_button = await self.page.query_selector('.send-btn')
            if send_button:
                await send_button.click()
                await AntiDetection.random_sleep(0.5, 1)

                logger.info(f"✅ 消息发送成功")
                return True
            else:
                logger.warning(f"⚠️ 未找到发送按钮")
                return False

        except Exception as e:
            logger.error(f"❌ 发送消息失败: {str(e)}")
            return False

    async def check_for_issues(self) -> Optional[str]:
        """
        检查是否出现验证码或账号限制

        Returns:
            如果有问题，返回问题描述；否则返回 None
        """
        # 检查验证码
        has_captcha = await AntiDetection.check_for_captcha(self.page)
        if has_captcha:
            return "检测到验证码"

        # 检查账号限制
        limit_reason = await AntiDetection.check_account_limit(self.page)
        if limit_reason:
            return f"账号被限制: {limit_reason}"

        return None

    async def cleanup(self):
        """清理资源，关闭浏览器"""
        logger.info("🔚 清理资源...")

        if self.page:
            await self.page.close()
            self.page = None

        if self.context:
            await self.context.close()
            self.context = None

        if self.browser:
            await self.browser.close()
            self.browser = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

        logger.info("✅ 资源清理完成")

    async def __aenter__(self):
        """上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        await self.cleanup()

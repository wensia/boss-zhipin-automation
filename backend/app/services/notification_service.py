"""
通知服务 - 钉钉机器人通知
"""
import time
import hmac
import hashlib
import base64
import urllib.parse
import json
import httpx
from typing import Optional

from app.models.notification_config import NotificationConfig


class NotificationService:
    """通知服务类"""

    def __init__(self, config: NotificationConfig):
        self.config = config

    def _get_signed_url(self, webhook: str, secret: Optional[str] = None) -> str:
        """
        生成带签名的钉钉 Webhook URL

        Args:
            webhook: 钉钉机器人 Webhook 地址
            secret: 签名密钥（可选）

        Returns:
            带签名的完整 URL
        """
        if not secret:
            return webhook

        # 生成时间戳
        timestamp = str(round(time.time() * 1000))

        # 拼接签名字符串
        secret_enc = secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')

        # 生成签名
        hmac_code = hmac.new(
            secret_enc,
            string_to_sign_enc,
            digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        # 拼接完整 URL
        return f'{webhook}&timestamp={timestamp}&sign={sign}'

    async def send_message(self, title: str, content: str) -> bool:
        """
        发送钉钉消息

        Args:
            title: 消息标题
            content: 消息内容

        Returns:
            是否发送成功
        """
        if not self.config.dingtalk_enabled:
            return False

        if not self.config.dingtalk_webhook:
            return False

        try:
            # 获取签名后的 URL
            url = self._get_signed_url(
                self.config.dingtalk_webhook,
                self.config.dingtalk_secret
            )

            # 构造消息体
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": f"### {title}\n\n{content}"
                }
            }

            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=message,
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get('errcode') == 0:
                        return True
                    else:
                        print(f"钉钉通知发送失败: {result.get('errmsg')}")
                        return False
                else:
                    print(f"钉钉通知请求失败: {response.status_code}")
                    return False

        except Exception as e:
            print(f"发送钉钉通知异常: {str(e)}")
            return False

    async def send_task_completion_notification(
        self,
        success_count: int,
        failed_count: int,
        skipped_count: int,
        total_processed: int,
        elapsed_time: float
    ) -> bool:
        """
        发送任务完成通知

        Args:
            success_count: 成功数
            failed_count: 失败数
            skipped_count: 跳过数
            total_processed: 总处理数
            elapsed_time: 耗时（秒）

        Returns:
            是否发送成功
        """
        if not self.config.notify_on_completion:
            return False

        title = "🎉 打招呼任务完成"
        content = f"""
**任务已完成**

- ✅ 成功：{success_count} 个
- ❌ 失败：{failed_count} 个
- ⏭️ 跳过：{skipped_count} 个
- 📊 共处理：{total_processed} 个候选人
- ⏱️ 耗时：{elapsed_time:.1f} 秒

> 完成时间：{time.strftime("%Y-%m-%d %H:%M:%S")}
"""

        return await self.send_message(title, content)

    async def send_limit_reached_notification(
        self,
        success_count: int,
        failed_count: int,
        skipped_count: int,
        total_processed: int
    ) -> bool:
        """
        发送触发限制通知

        Args:
            success_count: 成功数
            failed_count: 失败数
            skipped_count: 跳过数
            total_processed: 总处理数

        Returns:
            是否发送成功
        """
        if not self.config.notify_on_limit:
            return False

        title = "⚠️ 打招呼已达上限"
        content = f"""
**检测到打招呼限制弹窗，任务已停止**

- ✅ 成功：{success_count} 个
- ❌ 失败：{failed_count} 个
- ⏭️ 跳过：{skipped_count} 个
- 📊 共处理：{total_processed} 个候选人

> 触发时间：{time.strftime("%Y-%m-%d %H:%M:%S")}

**建议：** 请稍后再试，或明天继续
"""

        return await self.send_message(title, content)

    async def send_error_notification(self, error_message: str) -> bool:
        """
        发送错误通知

        Args:
            error_message: 错误信息

        Returns:
            是否发送成功
        """
        if not self.config.notify_on_error:
            return False

        title = "❌ 任务执行出错"
        content = f"""
**任务执行过程中发生错误**

错误信息：
```
{error_message}
```

> 发生时间：{time.strftime("%Y-%m-%d %H:%M:%S")}
"""

        return await self.send_message(title, content)

    async def send_test_message(self) -> bool:
        """
        发送钉钉测试消息

        Returns:
            是否发送成功
        """
        title = "🔔 钉钉通知测试"
        content = f"""
**这是一条测试消息**

如果你收到这条消息，说明钉钉机器人配置正确！

> 发送时间：{time.strftime("%Y-%m-%d %H:%M:%S")}
"""

        return await self.send_message(title, content)

    async def send_feishu_message(self, title: str, content: str) -> bool:
        """
        发送飞书消息

        Args:
            title: 消息标题
            content: 消息内容

        Returns:
            是否发送成功
        """
        if not self.config.feishu_enabled:
            return False

        if not self.config.feishu_webhook:
            return False

        try:
            # 获取签名后的 URL (如果有签名密钥)
            url = self._get_feishu_signed_url(
                self.config.feishu_webhook,
                self.config.feishu_secret
            )

            # 构造消息体 - 飞书使用富文本格式
            message = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": title
                        },
                        "template": "blue"
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": content
                        },
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "content": f"发送时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
                                }
                            ]
                        }
                    ]
                }
            }

            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=message,
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    result = response.json()
                    # 飞书返回的成功码是 0
                    if result.get('code') == 0 or result.get('StatusCode') == 0:
                        return True
                    else:
                        print(f"飞书通知发送失败: {result.get('msg', result.get('StatusMessage'))}")
                        return False
                else:
                    print(f"飞书通知请求失败: {response.status_code}")
                    return False

        except Exception as e:
            print(f"发送飞书通知异常: {str(e)}")
            return False

    def _get_feishu_signed_url(self, webhook: str, secret: Optional[str] = None) -> str:
        """
        生成带签名的飞书 Webhook URL

        Args:
            webhook: 飞书机器人 Webhook 地址
            secret: 签名密钥（可选）

        Returns:
            带签名的完整 URL（如果有密钥）或原始 URL
        """
        if not secret:
            return webhook

        # 飞书的签名方式：生成时间戳和签名
        timestamp = str(int(time.time()))

        # 拼接签名字符串
        string_to_sign = f'{timestamp}\n{secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')

        # 生成签名
        hmac_code = hmac.new(
            secret.encode('utf-8'),
            string_to_sign_enc,
            digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')

        # 返回原始 URL（签名在请求体中）
        return webhook

    async def send_feishu_test_message(self) -> bool:
        """
        发送飞书测试消息

        Returns:
            是否发送成功
        """
        title = "🔔 飞书通知测试"
        content = """**这是一条测试消息**

如果你收到这条消息，说明飞书机器人配置正确！

✅ 配置验证成功
📱 消息推送正常
"""

        # 如果有签名密钥，需要在消息体中添加签名信息
        if self.config.feishu_secret:
            timestamp = str(int(time.time()))
            string_to_sign = f'{timestamp}\n{self.config.feishu_secret}'
            hmac_code = hmac.new(
                self.config.feishu_secret.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
            sign = base64.b64encode(hmac_code).decode('utf-8')

            # 使用带签名的消息格式
            try:
                url = self.config.feishu_webhook
                message = {
                    "timestamp": timestamp,
                    "sign": sign,
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {
                                "tag": "plain_text",
                                "content": title
                            },
                            "template": "blue"
                        },
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": content
                            },
                            {
                                "tag": "note",
                                "elements": [
                                    {
                                        "tag": "plain_text",
                                        "content": f"发送时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
                                    }
                                ]
                            }
                        ]
                    }
                }

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        json=message,
                        headers={"Content-Type": "application/json"},
                        timeout=10.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        if result.get('code') == 0 or result.get('StatusCode') == 0:
                            return True
                        else:
                            print(f"飞书通知发送失败: {result.get('msg', result.get('StatusMessage'))}")
                            return False
                    else:
                        print(f"飞书通知请求失败: {response.status_code}")
                        return False

            except Exception as e:
                print(f"发送飞书通知异常: {str(e)}")
                return False
        else:
            # 没有签名密钥，使用简单格式
            return await self.send_feishu_message(title, content)

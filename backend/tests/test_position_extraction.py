"""
测试期望职位提取逻辑
对比不同的提取方法
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def test_extraction_methods():
    """测试不同的期望职位提取方法"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            storage_state='boss_auth.json'
        )
        page = await context.new_page()

        print("🔍 导航到推荐牛人页面")
        await page.goto('https://www.zhipin.com/web/chat/recommend', wait_until='networkidle')
        await asyncio.sleep(3)

        # 找到 recommendFrame
        recommend_frame = None
        for frame in page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            print("❌ 未找到 recommendFrame")
            await browser.close()
            return

        print("✅ 找到 recommendFrame")
        await asyncio.sleep(2)

        # 获取第一个候选人卡片
        card = recommend_frame.locator('ul.card-list > li:nth-child(1)').first

        print("\n" + "="*80)
        print("测试方法1: 使用 inner_text() + split('·')")
        print("="*80)

        try:
            expect_row = card.locator('.row-flex .content .join-text-wrap').first
            if await expect_row.count() > 0:
                text = await expect_row.inner_text()
                print(f"原始文本: '{text}'")
                print(f"文本长度: {len(text)}")
                print(f"文本的 repr: {repr(text)}")

                parts = text.split('·')
                print(f"split('·') 结果: {parts}")
                print(f"parts 长度: {len(parts)}")

                if len(parts) > 1:
                    position = parts[1].strip()
                    print(f"✅ 提取的职位: '{position}'")
                else:
                    print("❌ 无法通过 split('·') 提取职位")
            else:
                print("❌ 未找到 expect_row 元素")
        except Exception as e:
            print(f"❌ 方法1失败: {e}")

        print("\n" + "="*80)
        print("测试方法2: 使用 JavaScript extractJoinTextParts (原脚本方法)")
        print("="*80)

        try:
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

                    const col2 = el.querySelector('.col-2');
                    if (!col2) return { error: 'col2 not found' };

                    const expectRow = col2.querySelector('.row-flex .content .join-text-wrap');
                    if (!expectRow) return { error: 'expectRow not found' };

                    const parts = extractJoinTextParts(expectRow);

                    return {
                        html: expectRow.innerHTML,
                        outerHTML: expectRow.outerHTML,
                        textContent: expectRow.textContent,
                        innerText: expectRow.innerText,
                        parts: parts,
                        expectedCity: parts[0] || null,
                        expectedPosition: parts[1] || null
                    };
                }
            """)

            print(f"HTML: {result.get('html')}")
            print(f"outerHTML: {result.get('outerHTML')}")
            print(f"textContent: {result.get('textContent')}")
            print(f"innerText: {result.get('innerText')}")
            print(f"提取的 parts: {result.get('parts')}")
            print(f"✅ 期望城市: '{result.get('expectedCity')}'")
            print(f"✅ 期望职位: '{result.get('expectedPosition')}'")

        except Exception as e:
            print(f"❌ 方法2失败: {e}")

        print("\n" + "="*80)
        print("测试方法3: 检查所有可能的选择器")
        print("="*80)

        try:
            selectors = [
                '.row-flex .content .join-text-wrap',
                '.col-2 .row-flex .content .join-text-wrap',
                '.join-text-wrap',
                '.geek-expect',
            ]

            for selector in selectors:
                print(f"\n尝试选择器: {selector}")
                elements = card.locator(selector)
                count = await elements.count()
                print(f"  找到 {count} 个元素")

                if count > 0:
                    for i in range(count):
                        elem = elements.nth(i)
                        text = await elem.inner_text()
                        print(f"  [{i}] 文本: '{text}'")
        except Exception as e:
            print(f"❌ 方法3失败: {e}")

        print("\n" + "="*80)
        print("测试完成！按回车键关闭浏览器...")
        input()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_extraction_methods())

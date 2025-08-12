import telegram
import asyncio
import os
import datetime
from pyppeteer import launch

# --- 你的 Telegram 配置 ---
BOT_TOKEN = "7876256245:AAEUELD5GRm0APzzlgozTy2rjBYIYw8Qzp4"
CHAT_ID = "-1002883960310"

async def send_telegram_message(html_content):
    """
    使用 pyppeteer 将HTML内容渲染为图片并发送到Telegram。
    这是包含所有修正的最终、健壮版本。
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 无法发送消息：Telegram Bot Token 或 Chat ID 未设置。")
        return

    bot = telegram.Bot(token=BOT_TOKEN)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    img_file = f"report_{timestamp}.png"
    
    browser = None # 先声明一个空的browser变量
    try:
        # 1. 启动浏览器
        print("🔄 正在启动浏览器以生成报告图片...")
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        await page.setViewport({'width': 800, 'height': 600})
        
        # 2. 设置内容并截图
        await page.setContent(html_content)
        await page.screenshot({'path': img_file, 'fullPage': True})
        print("✅ 图片生成成功。")
        
        # 3. 发送图片
        with open(img_file, 'rb') as photo:
            await bot.send_photo(
                chat_id=CHAT_ID, 
                photo=photo,
                caption="🚨 每日市场情报摘要"
            )
        
        print("✅ 报告已作为图片发送至Telegram。")

    except Exception as e:
        print(f"❌ 生成或发送图片时出错: {e}")
    
    finally:
        # 4. 无论成功还是失败，最后都确保关闭浏览器和清理文件
        if browser:
            await browser.close()
            print("✅ 浏览器已成功关闭。")
        if os.path.exists(img_file):
            os.remove(img_file)

# --- 测试模块 ---
if __name__ == '__main__':
    test_html = "<h1>最终方案测试</h1><p>这是一个使用 <strong>pyppeteer</strong> 生成的最终报告。</p>"
    asyncio.run(send_telegram_message(test_html))
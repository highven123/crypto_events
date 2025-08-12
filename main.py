import asyncio
from data_storage import store_news_item, clear_stored_news
# --- [核心修改] 替换导入源 ---
from news_api_scraper import fetch_crypto_news

async def main():
    """
    主程序，协调从 NewsAPI 采集新闻并存储。
    """
    # --- [核心修改] 调用新的新闻获取函数 ---
    news_list = fetch_crypto_news()
    
    if not news_list:
        print("❌ 未能从 NewsAPI 获取到新闻，程序退出。")
        return

    # 每次获取新数据前先清空旧数据
    clear_stored_news() 
    
    # 将新闻保存到本地CSV文件
    for news_item in news_list:
        # --- [核心修改] 将 description 映射到 body ---
        store_news_item(
            title=news_item.get('title'),
            source=news_item.get('source'),
            body=news_item.get('description') # 使用 description 作为新闻主体内容
        )
    
    print(f"✅ 成功从 NewsAPI 获取并存储 {len(news_list)} 条新闻。")

if __name__ == '__main__':
    asyncio.run(main())
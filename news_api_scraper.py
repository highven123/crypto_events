import requests
import os
from datetime import datetime, timedelta

# --- 配置区 ---
# 你的NewsAPI.org API Key
API_KEY = "d362bec904e643558c837840011cc706"

# --- [核心修改] 升级关键词和搜索逻辑 ---
# 关键词必须出现在标题中，内容更聚焦
SEARCH_KEYWORDS_IN_TITLE = '(crypto OR cryptocurrency OR bitcoin OR ethereum OR BTC OR ETH OR blockchain OR web3 OR defi)'

EXCLUDED_DOMAINS = "gizmodo.com" 
LANGUAGE = "en"
PAGE_SIZE = 20

def fetch_crypto_news():
    """
    使用NewsAPI获取最新的、标题相关的加密货币新闻。
    """
    if not API_KEY:
        print("❌ NewsAPI Key未设置，无法获取新闻。")
        return []

    print("🔄 [新赛道 V2] 正在通过 NewsAPI 获取全球宏观新闻 (已开启标题精准过滤)...")
    
    url = "https://newsapi.org/v2/everything"
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # --- [核心修改] 使用 qInTitle 参数进行精准搜索 ---
    params = {
        'qInTitle': SEARCH_KEYWORDS_IN_TITLE, # 只搜索标题
        'language': LANGUAGE,
        'sortBy': 'publishedAt',
        'pageSize': PAGE_SIZE,
        'from': yesterday,
        'excludeDomains': EXCLUDED_DOMAINS,
    }
    
    headers = {
        'Authorization': API_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            news_list = []
            for article in articles:
                news_list.append({
                    "source": article.get("source", {}).get("name", "N/A"),
                    "title": article.get("title", "N/A"),
                    "description": article.get("description", "N/A"),
                    "url": article.get("url", "#"),
                    "published_at": article.get("publishedAt", "N/A"),
                })
            print(f"✅ 成功从 NewsAPI 获取到 {len(news_list)} 条高度相关新闻。")
            return news_list
        else:
            print(f"❌ NewsAPI 返回错误: {data.get('message')}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求NewsAPI时发生网络错误: {e}")
        return []
    except Exception as e:
        print(f"❌ 处理新闻数据时发生未知错误: {e}")
        return []

# --- 测试模块 ---
if __name__ == '__main__':
    latest_news = fetch_crypto_news()
    if latest_news:
        print("\n--- 高度相关的加密货币新闻预览 ---")
        for i, news in enumerate(latest_news[:5]):
            print(f"{i+1}. {news['title']} (来源: {news['source']})")
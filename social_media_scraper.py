import snscrape.modules.twitter as sntwitter
import datetime

# --- 第一阶段：新增的配置项 ---

# 1. 发布者硬指标筛选阈值
MIN_FOLLOWER_COUNT = 1000  # 用户的最低粉丝数
MIN_ACCOUNT_AGE_DAYS = 180 # 账户的最短注册天数 (约6个月)

# 2. 关键词搜索的通用过滤指令 (会自动附加到每个关键词后面)
KEYWORD_FILTERS = "min_faves:10 lang:en" # 至少10个点赞，且语言为英文

# 3. 监控目标列表
KOL_ACCOUNTS = [
    "VitalikButerin", "saylor", "a16zcrypto", "arthurhayes", "elonmusk",
    "woonomic", "lookonchain", "realDonaldTrump",
]

KEYWORDS_TO_TRACK = [
    "RWA", "DePIN", "AI crypto", "Restaking", "airdrop", "$SOL", "$TON",
]

# 4. 每个查询的抓取数量上限
LIMIT_PER_QUERY = 10 # 适当增加上限，因为很多会被过滤掉

def scrape_social_media_feeds():
    """
    使用snscrape抓取信息，并应用第一阶段的过滤规则。
    """
    print("🔄 [第一阶段] 启动社交媒体信息抓取 (已开启预过滤)...")
    all_posts = []
    
    # --- 抓取KOL的推文 (不进行额外过滤) ---
    print(f"🎤 正在抓取 {len(KOL_ACCOUNTS)} 位核心KOL的推文...")
    for username in KOL_ACCOUNTS:
        try:
            scraper = sntwitter.TwitterUserScraper(username)
            for i, tweet in enumerate(scraper.get_items()):
                if i >= LIMIT_PER_QUERY:
                    break
                all_posts.append(f"来自核心KOL {username} 的推文: {tweet.rawContent}")
        except Exception as e:
            print(f"❌ 抓取用户 {username} 时出错: {e}")

    # --- 抓取关键词相关的推文 (应用硬指标过滤) ---
    print(f"🔍 正在抓取 {len(KEYWORDS_TO_TRACK)} 个关键词的讨论 (将进行严格筛选)...")
    # 获取当前的UTC时间，用于计算账户年龄
    now = datetime.datetime.now(datetime.timezone.utc)

    for keyword in KEYWORDS_TO_TRACK:
        # 构造带有高级过滤指令的搜索查询
        advanced_query = f'"{keyword}" {KEYWORD_FILTERS}'
        print(f"  -> 正在搜索: {advanced_query}")
        try:
            scraper = sntwitter.TwitterSearchScraper(advanced_query)
            for i, tweet in enumerate(scraper.get_items()):
                if i >= (LIMIT_PER_QUERY * 5): # 扩大搜索范围，因为很多会被过滤
                    break
                
                # --- [核心过滤逻辑] ---
                # 1. 筛选账户年龄
                account_age_days = (now - tweet.user.created).days
                if account_age_days < MIN_ACCOUNT_AGE_DAYS:
                    # print(f"  -> 过滤: 作者({tweet.user.username})注册时间({account_age_days}天)过短。")
                    continue # 跳过这条推文

                # 2. 筛选粉丝数
                if tweet.user.followersCount < MIN_FOLLOWER_COUNT:
                    # print(f"  -> 过滤: 作者({tweet.user.username})粉丝数({tweet.user.followersCount})过低。")
                    continue # 跳过这条推文
                
                # 如果通过所有筛选，则采纳该信息
                all_posts.append(f"关于'{keyword}'的高质量讨论: {tweet.rawContent}")

                # 限制每个关键词最终只采纳几条高质量信息
                if len([p for p in all_posts if f"'{keyword}'" in p]) >= LIMIT_PER_QUERY:
                    break

        except Exception as e:
            print(f"❌ 抓取关键词 '{keyword}' 时出错: {e}")
    
    if all_posts:
        print(f"✅ [第一阶段] 过滤完成，成功捕获 {len(all_posts)} 条高质量动态。")
    else:
        print("⚠️ [第一阶段] 未捕获到任何符合条件的高质量信息。")
            
    return all_posts

# --- 测试模块 ---
if __name__ == '__main__':
    latest_posts = scrape_social_media_feeds()
    if latest_posts:
        print("\n--- [第一阶段] 筛选后的高质量动态预览 ---")
        for post in latest_posts:
            print(f"- {post[:150]}...")
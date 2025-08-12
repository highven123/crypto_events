import pandas as pd
from pytrends.request import TrendReq
import time

# --- 配置区 ---
# 我们想要追踪的关键词
TREND_KEYWORDS = ['bitcoin', 'ethereum', 'crypto airdrop', 'RWA', 'web3']
# 分析的时间范围，例如 'today 1-m' 表示过去一个月
TIME_FRAME = 'today 1-m' 

def get_google_trends_insights():
    """
    获取并分析Google Trends数据，识别热度变化趋势。
    """
    print(f"🔄 [新赛道] 正在通过 Google Trends 获取 {len(TREND_KEYWORDS)} 个关键词的市场关注度...")
    
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        insights = []

        for keyword in TREND_KEYWORDS:
            pytrends.build_payload([keyword], cat=0, timeframe=TIME_FRAME, geo='', gprop='')
            # 获取数据
            interest_over_time_df = pytrends.interest_over_time()
            
            if interest_over_time_df.empty:
                continue

            # --- 核心分析逻辑：对比最近7天和整个周期的平均热度 ---
            # 移除值为0的行，因为Google Trends在无数据时会返回0
            interest_over_time_df = interest_over_time_df[interest_over_time_df[keyword] > 0]
            
            if len(interest_over_time_df) < 7: # 数据点太少，无法分析
                continue

            # 计算整个周期的平均值
            period_average = interest_over_time_df[keyword].mean()
            # 计算最近7天的平均值
            last_7_days_average = interest_over_time_df[keyword].tail(7).mean()

            # 判断趋势
            trend_desc = "平稳"
            percentage_change = 0
            if period_average > 0:
                percentage_change = ((last_7_days_average - period_average) / period_average) * 100
                if percentage_change > 30:
                    trend_desc = f"显著上升(↑ {percentage_change:.0f}%)"
                elif percentage_change < -30:
                    trend_desc = f"显著下降(↓ {percentage_change:.0f}%)"
            
            insight_text = f"关键词'{keyword}'的公众关注度趋势: {trend_desc}"
            insights.append(insight_text)
            
            # 遵守谷歌的请求频率，每次查询后稍作等待
            time.sleep(1)

        print(f"✅ 成功分析 Google Trends 市场关注度。")
        return insights

    except Exception as e:
        print(f"❌ 获取Google Trends数据时出错: {e}")
        return []

# --- 测试模块 ---
if __name__ == '__main__':
    trends_insights = get_google_trends_insights()
    if trends_insights:
        print("\n--- 谷歌趋势分析洞察 ---")
        for insight in trends_insights:
            print(f"- {insight}")
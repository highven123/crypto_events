import google.generativeai as genai
import os
import json
import asyncio
from data_storage import get_all_stored_news, clear_stored_news
from funding_rate_monitor import get_multi_exchange_funding_rates
from notifier import send_telegram_message
from onchain_monitor import get_large_eth_transfers
# --- [最终整合] 导入所有数据源 ---
from main import main 
from google_trends_monitor import get_google_trends_insights

# --- 配置API Key ---
genai.configure(api_key="AIzaSyDNpJUBeAc08-MCnXyaCZz3xNHVA2SaAPA") # 请替换为你的真实Key
model = genai.GenerativeModel('gemini-1.5-flash')

# --- [最终整合] 函数签名加入 trends_insights ---
def summarize_market_review(news_list, funding_rates_data, onchain_data, trends_insights):
    """
    使用 Gemini 模型对新闻、资金费率、链上数据和谷歌趋势进行综合总结。
    """
    if not news_list:
        return None

    # 格式化所有新闻内容
    all_news_text = ""
    for idx, news_item in enumerate(news_list):
        all_news_text += f"--- 新闻 {idx + 1} ---\n标题: {news_item.get('title', '无标题')}\n来源: {news_item.get('source', '未知')}\n内容: {news_item.get('body', '无内容')}\n\n"

    # 格式化资金费率数据
    funding_rates_text = "【资金费率数据】\n"
    if funding_rates_data:
        for ex_name, data in funding_rates_data.items():
            if data and 'rate' in data:
                rate_value = data['rate']
                sentiment_note = "中性"
                if rate_value > 0.0002: sentiment_note = "看涨 (多头杠杆较高)"
                elif rate_value < -0.0002: sentiment_note = "看跌 (空头杠杆较高)"
                funding_rates_text += f"- {ex_name}: {rate_value:.6f} -> {sentiment_note}\n"
    
    # 格式化链上数据
    onchain_text = "【链上大额转账数据】\n"
    if onchain_data:
        for idx, tx in enumerate(onchain_data):
            onchain_text += f"- 交易 {idx + 1}: 金额 {tx['eth_amount']:.2f} ETH 从 {tx['from'][:8]}... 到 {tx['to'][:8]}...\n"
    else:
        onchain_text += "近期无大额转账。\n"

    # --- [最终整合] 格式化谷歌趋势数据 ---
    google_trends_text = "【市场关注度趋势】\n"
    if trends_insights:
        for insight in trends_insights:
            google_trends_text += f"{insight}\n"
    else:
        google_trends_text += "未能获取到有效的关注度数据。\n"

    # --- [最终整合] 更新Prompt，加入谷歌趋势分析指令 ---
    prompt = f"""
你是一位顶尖的加密货币市场宏观分析师，擅长结合多维度信息进行市场洞察。你的任务是根据以下提供的专业新闻、资金费率、链上数据和谷歌趋势数据，生成一份精炼、专业的市场总结报告。

请严格遵守以下指令：
1. **综合分析**: 结合所有信息，特别是将谷歌趋势作为大众情绪的参考，与专业新闻和链上数据（聪明钱动向）进行对比分析。
2. **风险与策略**: 在最终总结中，必须明确指出当前市场的**风险等级**，并提供一条**具体的、可执行的交易策略**。
3. **严格的 JSON 格式输出**: 你的最终输出必须是一个只包含 JSON 对象的纯文本。

【信息汇总】
{all_news_text}
{funding_rates_text}
{onchain_text}
{google_trends_text}

请提供你的总结报告，以 JSON 格式输出，包含以下两个主要部分：
- "news_analyses": 一个列表，每个元素包含 "title", "summary", "sentiment", "reason" 和 "affected_tokens" 字段。
- "final_summary": 一个JSON对象，包含 "overall_sentiment", "overall_strength", "overall_action", "overall_reason", "risk_level" 和 "strategy_suggestion" 字段。
"""
    try:
        response = model.generate_content(prompt)
        analysis_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        analysis_json = json.loads(analysis_text)
        return analysis_json
    except Exception as e:
        print(f"❌ Gemini模型调用或解析时出错: {e}")
        # 增加打印原始返回文本的逻辑，便于调试
        if 'response' in locals() and hasattr(response, 'text'):
            print("--- Gemini返回的原始文本如下 ---")
            print(response.text)
            print("-----------------------------")
        return None

def format_summary_for_telegram(summary_data):
    """
    将AI返回的JSON数据格式化为HTML内容。
    """
    if not summary_data:
        return "<p>无法生成报告，数据为空。</p>"

    html = "<div style='font-family: sans-serif;'>"
    html += "<h2 style='color: #333;'>🚨 每日市场情报摘要 🚨</h2>"

    if 'news_analyses' in summary_data and summary_data['news_analyses']:
        html += "<h3>--- 核心事件洞察 ---</h3>"
        for idx, analysis in enumerate(summary_data['news_analyses']):
            affected_tokens = ', '.join(analysis.get('affected_tokens', [])) if analysis.get('affected_tokens') else 'N/A'
            html += f"<div><strong>{idx + 1}. {analysis.get('title', 'N/A')}</strong></div>"
            html += f"<div><strong>情绪:</strong> {analysis.get('sentiment', 'N/A')}</div>"
            html += f"<div><strong>影响:</strong> {affected_tokens}</div>"
            html += f"<div><strong>摘要:</strong> {analysis.get('summary', 'N/A')}</div><br/>"

    if 'final_summary' in summary_data and summary_data['final_summary']:
        final_summary = summary_data['final_summary']
        html += "<h3>--- 宏观市场总结 ---</h3>"
        html += f"<div><strong>整体情绪:</strong> {final_summary.get('overall_sentiment', 'N/A')} (强度: {final_summary.get('overall_strength', 'N/A')})</div>"
        html += f"<div><strong>核心逻辑:</strong> {final_summary.get('overall_reason', 'N/A')}</div>"
        html += f"<div><strong>风险等级:</strong> <strong style='color: red;'>{final_summary.get('risk_level', 'N/A')}</strong></div><br/>"
        html += f"<div><strong>▶️ 操作建议:</strong> <strong style='color: green;'>{final_summary.get('overall_action', 'N/A')}</strong></div>"
        html += f"<div><strong>💡 策略详情:</strong> {final_summary.get('strategy_suggestion', 'N/A')}</div>"

    html += "</div>"
    return html

async def run_summary_report():
    """
    运行完整的总结报告生成流程。
    """
    # 1. 获取专业新闻
    await main()
    news_items = get_all_stored_news()
    if not news_items:
        print("💡 未收集到新事件，跳过生成总结报告。")
        return

    # 2. 获取其他维度数据
    funding_rates = get_multi_exchange_funding_rates()
    onchain_transfers = get_large_eth_transfers(min_eth_amount=10)
    # --- [最终整合] 调用谷歌趋势分析函数 ---
    trends_insights = get_google_trends_insights()
    
    print(f"✅ 所有情报源采集完毕: {len(news_items)}条新闻, 链上数据, 资金费率, 谷歌趋势。")
    print("🚀 正在调用AI进行终极综合分析...")
    
    # 3. 调用AI进行综合分析
    summary_data = summarize_market_review(news_items, funding_rates, onchain_transfers, trends_insights)
    
    if summary_data:
        print("✅ 终极分析报告生成成功。")
        html_message = format_summary_for_telegram(summary_data)
        await send_telegram_message(html_message) # 传递 HTML 内容
        clear_stored_news()
        print("✅ 本地新闻数据已清空。")
    else:
        print("❌ 终极分析报告生成失败。")

if __name__ == '__main__':
    # 注意：format_summary_for_telegram 函数的完整定义需要从之前的回答中复制过来
    def format_summary_for_telegram(summary_data):
        if not summary_data: return "无法生成报告，数据为空。"
        message = "🚨 **每日市场情报摘要** 🚨\n\n"
        if 'news_analyses' in summary_data and summary_data['news_analyses']:
            message += "--- **核心事件洞察** ---\n"
            for idx, analysis in enumerate(summary_data['news_analyses']):
                affected_tokens = ', '.join(analysis.get('affected_tokens', [])) if analysis.get('affected_tokens') else 'N/A'
                message += f"**{idx + 1}. {analysis.get('title', 'N/A')}**\n"
                message += f"   - **情绪**: {analysis.get('sentiment', 'N/A')}\n"
                message += f"   - **影响**: {affected_tokens}\n"
                message += f"   - **摘要**: {analysis.get('summary', 'N/A')}\n\n"
        if 'final_summary' in summary_data and summary_data['final_summary']:
            final_summary = summary_data['final_summary']
            message += "--- **宏观市场总结** ---\n"
            message += f"**整体情绪**: {final_summary.get('overall_sentiment', 'N/A')} (强度: {final_summary.get('overall_strength', 'N/A')})\n"
            message += f"**核心逻辑**: {final_summary.get('overall_reason', 'N/A')}\n"
            message += f"**风险等级**: **{final_summary.get('risk_level', 'N/A')}**\n\n"
            message += f"**▶️ 操作建议: {final_summary.get('overall_action', 'N/A')}**\n"
            message += f"**💡 策略详情**: {final_summary.get('strategy_suggestion', 'N/A')}\n"
        return message
    asyncio.run(run_summary_report())
import google.generativeai as genai
import json
from datetime import datetime

# --- 1. 配置你的API Key ---
# 请在这里替换成你自己的Gemini API Key
GOOGLE_API_KEY = 'AIzaSyDNpJUBeAc08-MCnXyaCZz3xNHVA2SaAPA' 
genai.configure(api_key=GOOGLE_API_KEY)


def analyze_crypto_news(title, body, funding_rates_data):
    """
    调用Gemini模型，结合新闻和资金费率进行综合分析
    """
    # 将资金费率数据格式化成AI易于理解的文本
    funding_rates_text = ""
    if funding_rates_data:
        funding_rates_text = "【实时资金费率数据】\n"
        for ex_name, data in funding_rates_data.items():
            if data and 'rate' in data:
                rate_value = data['rate']
                sentiment_note = "中性 (Neutral)"
                if rate_value > 0.0002:
                    sentiment_note = "看涨 (Bullish, 多头杠杆较高)"
                elif rate_value < -0.0002:
                    sentiment_note = "看跌 (Bearish, 空头杠杆较高)"
                
                funding_rates_text += f"- 交易所: {ex_name}, 资金费率: {rate_value:.6f} -> 市场情绪: {sentiment_note}\n"

    # --- 2. 精心设计的“分析指令”(Prompt) ---
    # 这就是你的核心竞争力，现在增加了对资金费率的分析指令
    PROMPT_TEMPLATE = f"""
你是一名顶尖的加密货币市场宏观分析师，擅长结合宏观新闻、市场数据和技术分析。
请分析以下新闻内容和实时资金费率数据，并严格按照JSON格式返回你的分析结果。

---
新闻标题：{title}
新闻内容：{body}
---

{funding_rates_text}

请回答以下问题，并以JSON对象格式输出：
1.  "sentiment": 结合新闻和资金费率，这条新闻对加密货币市场整体情绪是 "利好(bullish)", "利空(bearish)", 还是 "中性(neutral)"?
2.  "strength": 情绪的强度是 "弱(weak)", "中(moderate)", 还是 "强(strong)"?
3.  "affected_tokens": 列出3个最可能受此新闻影响的核心币种代码（例如：["BTC", "ETH"]）。
4.  "action_suggestion": 基于你的综合判断，你建议的操作是 "做多(long)", "做空(short)", "观望(observe)", 还是 "逢低吸纳(buy_the_dip)"?
5.  "reason": 用一句话简明扼要地解释你的判断依据。
"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = PROMPT_TEMPLATE.format(title=title, body=body)
        
        response = model.generate_content(prompt)
        
        json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
        analysis_result = json.loads(json_str)
        return analysis_result

    except Exception as e:
        print(f"调用API或解析JSON时出错: {e}")
        return None

# --- 3. 我们的第一个测试用例 (手动输入) ---
if __name__ == "__main__":
    test_title = "美联储主席鲍威尔发表鹰派讲话，暗示为抑制通胀，加息周期可能尚未结束"
    test_body = "在杰克逊霍尔全球央行年会上，美联储主席鲍威尔强调，尽管已取得进展，但通胀率仍远高于2%的目标。他表示，美联储准备在适当的情况下进一步加息，并打算将政策利率维持在限制性水平，直到确信通胀持续下降。"
    
    # 模拟一份实时资金费率数据
    mock_funding_rates = {
        'binance': {'rate': 0.000185, 'timestamp': datetime.now().isoformat()},
        'okx': {'rate': 0.000210, 'timestamp': datetime.now().isoformat()},
        'bybit': {'rate': 0.000195, 'timestamp': datetime.now().isoformat()}
    }

    print("正在分析新闻和市场数据...")
    print(f"标题: {test_title}\n")
    
    # 调用新的分析函数，传入资金费率数据
    result = analyze_crypto_news(test_title, test_body, mock_funding_rates)
    
    if result:
        print("--- 综合分析结果 ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("-----------------")
        print("\n核心逻辑验证成功！下一步可以接入真实数据源和推送模块。")
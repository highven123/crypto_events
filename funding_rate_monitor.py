import ccxt
from datetime import datetime

def get_multi_exchange_funding_rates():
    """
    使用 ccxt 库从多个主流交易所获取指定交易对的实时资金费率。
    """
    # 仅保留可以成功获取数据的交易所
    exchanges = {
        'binance': ccxt.binance(),
        'okx': ccxt.okx(),
        'bybit': ccxt.bybit(),
        'bitget': ccxt.bitget(),
    }
    
    # 针对不同交易所的特定永续合约符号进行适配
    symbols = {
        'binance': 'BTC/USDT:USDT',
        'okx': 'BTC-USDT-SWAP', # 修正 OKX 的永续合约符号
        'bybit': 'BTC/USDT:USDT',
        'bitget': 'BTC/USDT:USDT',
    }
    
    all_rates = {}
    
    for ex_name, exchange in exchanges.items():
        all_rates[ex_name] = {}
        symbol = symbols.get(ex_name)
        if not symbol:
            continue
        
        try:
            print(f"尝试从 {ex_name} 获取 {symbol} 的资金费率...")
            latest_rate = exchange.fetch_funding_rate(symbol)
            
            if latest_rate and latest_rate.get('fundingRate') is not None:
                timestamp = latest_rate.get('timestamp')
                timestamp_iso = datetime.fromtimestamp(timestamp / 1000).isoformat() if timestamp else datetime.now().isoformat()
                
                all_rates[ex_name] = {
                    "rate": latest_rate['fundingRate'],
                    "timestamp": timestamp_iso,
                }
            else:
                all_rates[ex_name] = None
                
        except Exception as e:
            print(f"❌ 获取 {ex_name} 上 {symbol} 的资金费率时出错: {e}")
            all_rates[ex_name] = None
                
    return all_rates

if __name__ == "__main__":
    rates = get_multi_exchange_funding_rates()
    
    if rates:
        print("\n✅ 成功获取最新资金费率：")
        for ex_name, data in rates.items():
            print(f"\n--- {ex_name} ---")
            if data:
                print(f"  费率: {data['rate']:.6f}")
                print(f"  时间戳: {data['timestamp']}")
            else:
                print(f"  数据获取失败")
    else:
        print("❌ 未能获取到任何资金费率信息。")
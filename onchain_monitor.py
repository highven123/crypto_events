import os
import requests
from datetime import datetime
import time
import random

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY') # <-- 修改为这行
COVALENT_API_KEY = os.getenv('COVALENT_API_KEY')  

def get_whale_addresses(min_eth_balance=1000, max_holders=100):
    """
    使用 Covalent API 获取 ETH 巨鲸钱包地址列表。
    """
    if not COVALENT_API_KEY:
        print("❌ Covalent API Key 未设置，无法获取巨鲸地址。")
        return []

    print(f"🔄 正在使用 Covalent API 获取持仓量前 {max_holders} 的巨鲸地址...")
    
    # Covalent API Endpoint: 获取代币持有者列表 (ETH)
    # ETH 的代币合约地址为 "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    url = f"https://api.covalenthq.com/v1/eth-mainnet/tokens/0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee/token_holders/?key={COVALENT_API_KEY}&page-size={max_holders}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        top_holders_list = []
        if data and data['data'] and data['data']['items']:
            for holder in data['data']['items']:
                balance_in_wei = int(holder.get('balance', 0))
                balance_in_eth = balance_in_wei / 10**18
                
                # 筛选出持仓量超过指定阈值的地址
                if balance_in_eth >= min_eth_balance:
                    top_holders_list.append(holder.get('address'))
        
        print(f"✅ 成功获取 {len(top_holders_list)} 个巨鲸地址。")
        return top_holders_list
    except Exception as e:
        print(f"❌ 调用 Covalent API 失败: {e}")
        return []


def get_large_eth_transfers(min_eth_amount=1000, max_transactions=50):
    """
    使用 Etherscan V2 API 监控巨鲸地址列表的最近大额 ETH 交易。
    """
    if not ETHERSCAN_API_KEY:
        print("❌ Etherscan API Key 未设置，无法监控链上数据。")
        return []

    # 动态获取巨鲸地址列表
    target_addresses = get_whale_addresses()
    
    # 如果没有获取到地址，就使用之前硬编码的交易所地址作为备选
    if not target_addresses:
        target_addresses = [
            "0x28C6c06298d514Db089934071355E5743bf21d60",
            "0x38600c822765d778d9b1399451996515b6d5f782"
        ]

    all_large_transfers = []
    
    print(f"✅ 成功获取 {len(target_addresses)} 个动态监控地址。")
    print(f"🚀 正在监控大额交易 (>{min_eth_amount} ETH)...")

    random.shuffle(target_addresses)
    
    for address in target_addresses:
        print(f" -> 正在查询地址: {address[:8]}...")
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "page": 1,
            "offset": max_transactions,
            "sort": "desc",
            "apikey": ETHERSCAN_API_KEY
        }
        
        try:
            response = requests.get(ETHERSCAN_API_URL, params=params)
            data = response.json()

            if data.get("status") == "1" and data.get("result"):
                for tx in data["result"]:
                    eth_amount = int(tx.get("value")) / 10**18
                    if eth_amount >= min_eth_amount:
                        all_large_transfers.append({
                            "tx_hash": tx.get("hash"),
                            "from": tx.get("from"),
                            "to": tx.get("to"),
                            "eth_amount": eth_amount,
                            "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp"))).isoformat()
                        })
            else:
                print(f"   ❌ API for {address[:8]}... returned: {data.get('message', '未知错误')}")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ 调用 Etherscan API 时出错: {e}")
            
    if all_large_transfers:
        print(f"✅ 成功获取 {len(all_large_transfers)} 条大额 ETH 转账信息。")
    else:
        print("💡 未发现符合条件的大额 ETH 转账。")

    return all_large_transfers

if __name__ == "__main__":
    transfers = get_large_eth_transfers(min_eth_amount=100, max_transactions=100)
    
    if transfers:
        print("\n--- 大额 ETH 转账列表 ---")
        for tx in transfers:
            print(f"时间: {tx['timestamp']}, 从: {tx['from'][:8]}..., 到: {tx['to'][:8]}..., 金额: {tx['eth_amount']:.2f} ETH")

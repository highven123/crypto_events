import pandas as pd
import os

NEWS_FILE = 'news_data.csv'

def store_news_item(title, source, body):
    """
    将单条新闻存储到CSV文件中。
    """
    # 检查文件是否存在，如果不存在则创建
    if not os.path.exists(NEWS_FILE):
        df = pd.DataFrame(columns=['title', 'source', 'body'])
        df.to_csv(NEWS_FILE, index=False)
    
    # 检查内容是否为空，如果为空则不存储
    if not title and not body:
        print("💡 忽略空新闻条目。")
        return

    # 将新数据添加到DataFrame
    new_item = pd.DataFrame([{'title': title, 'source': source, 'body': body}])
    new_item.to_csv(NEWS_FILE, mode='a', header=False, index=False)
    
def get_all_stored_news():
    """
    从CSV文件中读取所有新闻，并返回一个列表。
    """
    if not os.path.exists(NEWS_FILE):
        return []

    try:
        df = pd.read_csv(NEWS_FILE)
        
        # 确保列名是正确的
        if not all(col in df.columns for col in ['title', 'source', 'body']):
            print("❌ CSV文件格式不正确，无法读取。")
            return []
            
        news_list = []
        for index, row in df.iterrows():
            # 确保每个字段都是字符串，并处理缺失值
            news_list.append({
                'title': str(row['title']) if pd.notna(row['title']) else '无标题',
                'source': str(row['source']) if pd.notna(row['source']) else '未知',
                'body': str(row['body']) if pd.notna(row['body']) else '无内容'
            })
            
        # 排除空新闻条目
        news_list = [item for item in news_list if item['title'] != '无标题' and item['body'] != '无内容']
        
        return news_list
        
    except Exception as e:
        print(f"❌ 读取CSV文件时出错: {e}")
        return []

def clear_stored_news():
    """
    清空CSV文件中的所有新闻。
    """
    if os.path.exists(NEWS_FILE):
        os.remove(NEWS_FILE)
        print("✅ 已清空本地新闻数据。")
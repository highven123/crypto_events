from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_miit_news_with_selenium():
    """
    使用 Selenium 从工业和信息化部网站抓取最新的新闻标题和链接。
    """
    url = "https://www.miit.gov.cn/jgsj/zcwj/index.html"
    base_url = "https://www.miit.gov.cn"

    chrome_options = Options()
    # 启用无头模式，如果你想看到浏览器运行，可以注释掉这一行
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        # 使用显式等待，直到新闻列表容器出现
        wait = WebDriverWait(driver, 10)
        news_list_container = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "comp_list_xl"))
        )

        news_items = news_list_container.find_elements(By.TAG_NAME, "li")

        scraped_news = []
        for item in news_items[:10]:
            link_tag = item.find_element(By.TAG_NAME, "a")
            title = link_tag.text.strip()
            href = link_tag.get_attribute("href")
            
            scraped_news.append({"title": title, "url": href})
        
        return scraped_news

    except Exception as e:
        print(f"抓取网页时出错：{e}")
        return []

    finally:
        driver.quit()

if __name__ == "__main__":
    print("正在使用 Selenium 抓取网页，这可能需要一些时间...")
    latest_news = scrape_miit_news_with_selenium()
    if latest_news:
        print("最新10条新闻：")
        for news in latest_news:
            print(f"标题：{news['title']}\n链接：{news['url']}\n---")
    else:
        print("未能获取到新闻信息。")
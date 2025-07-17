import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
import os
from dotenv import load_dotenv
import time # 導入 time 模組
import random # 導入 random 模組

# 加載 .env 文件中的環境變量
load_dotenv()

def scrape_manhuagui_list(url):
    """
    抓取指定 URL 的內容，並使用 BeautifulSoup 處理後印出 li 節點，
    並將抓取到的數據寫入 MySQL 資料庫。
    Args:
        url (str): 要抓取的網頁 URL。
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    conn = None
    cursor = None
    try:
        # 從環境變量中獲取資料庫連接信息
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")

        # 連接到 MySQL 資料庫
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 檢查 HTTP 請求是否成功

        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到所有 li 節點
        li_nodes = soup.find_all('li')

        for li in li_nodes:
            try:
                book_url_raw = li.find('a', class_='bcover')['href'] if li.find('a', class_='bcover') else 'N/A'
                book_url = f"https://www.manhuagui.com{book_url_raw}" if book_url_raw != 'N/A' else 'N/A'

                book_id_match = re.search(r'/comic/(\d+)/', book_url)
                book_id = int(book_id_match.group(1)) if book_id_match else None # 將 book_id 轉換為 int，如果為 'N/A' 則為 None
                book_cover = f"https://cf.mhgui.com/cpic/b/{book_id}.jpg" if book_id is not None else 'N/A'

                book_name_tag = li.find('p', class_='ell').find('a')
                book_name = book_name_tag['title'] if book_name_tag and 'title' in book_name_tag.attrs else (book_name_tag.text.strip() if book_name_tag else 'N/A')

                last_update_tag = li.find('span', class_='updateon')
                last_update_full = last_update_tag.text.strip() if last_update_tag else 'N/A'
                
                last_update = None # 將 'N/A' 設置為 None，以便於資料庫處理 DATE 類型
                if '更新于：' in last_update_full:
                    date_part = last_update_full.split('更新于：')[1]
                    match = re.search(r'\d{4}-\d{2}-\d{2}', date_part)
                    if match:
                        last_update = match.group(0)

                # print(f"book_url: {book_url}")
                # print(f"book_name: {book_name}")
                # print(f"book_id: {book_id}")
                # print(f"book_cover: {book_cover}")
                # print(f"last_update: {last_update}")
                # print("-" * 30) # 分隔線

                # 將數據插入資料庫
                if book_id is not None: # 只有當 book_id 有效時才插入
                    insert_sql = """
                        INSERT INTO books (book_id, book_name, book_url, book_cover, last_update)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            book_name = VALUES(book_name),
                            book_url = VALUES(book_url),
                            book_cover = VALUES(book_cover),
                            last_update = VALUES(last_update)
                    """
                    cursor.execute(insert_sql, (book_id, book_name, book_url, book_cover, last_update))
                    conn.commit()
                    print(f"數據已成功插入/更新到資料庫: {book_name}")

            except AttributeError:
                # 某些 li 節點可能不包含所有預期的元素，跳過這些節點
                print("AttributeError: 跳過此 li 節點")
                continue
            except TypeError:
                # 處理可能出現的 NoneType 錯誤
                print("TypeError: 跳過此 li 節點")
                continue
            except mysql.connector.Error as err:
                print(f"資料庫錯誤: {err}")
                conn.rollback() # 回滾事務以防錯誤

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")
    except mysql.connector.Error as err:
        print(f"資料庫連接錯誤: {err}")
    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("資料庫連接已關閉。")

if __name__ == "__main__":
    base_url = "https://www.manhuagui.com/list/index_p{}.html"
    start_page = 1
    end_page = 1392

    test_counter = 0
    for page_num in range(start_page, end_page + 1):
        url = base_url.format(page_num)
        print(f"正在抓取頁面: {url}")
        scrape_manhuagui_list(url)
        print("-" * 50) # 頁面分隔線
        time.sleep(random.randint(3, 10)) # 每一頁抓取完畢後隨機休息 3 到 10 秒
        
        # test_counter += 1
        # if test_counter > 3:
        #     print("測試計數器已超過 3，跳出迴圈。")
        #     break

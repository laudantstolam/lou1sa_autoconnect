import os
from bs4 import BeautifulSoup
import pandas as pd
import re

def parse_time(time_str):
    """解析營業時間字串，返回開始和結束時間"""
    # 移除特殊字符和空白
    time_str = time_str.replace('週一至週日', '').strip()
    
    # 尋找時間pattern
    time_pattern = r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})'
    match = re.search(time_pattern, time_str)
    
    if match:
        return match.group(1), match.group(2)
    return '', ''  # 如果無法解析則返回空字串

def extract_phone(store_info):
    """從store_info中提取電話號碼"""
    phone_tag = store_info.find('p', string=lambda text: text and '電話' in text if text else False)
    if phone_tag:
        # 移除 "電話/" 並清理空白
        phone = phone_tag.text.replace('電話/', '').strip()
        return phone
    return ''

def process_html_file(file_path):
    """處理單個HTML檔案並返回店鋪資訊列表"""
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
    
    stores = []
    # 找出所有包含門市資訊的row
    store_rows = soup.find_all('div', class_='row')
    
    for row in store_rows:
        # 檢查這個row是否包含store_info
        store_info = row.find('div', class_='store_info')
        if not store_info:
            continue
            
        # 找到該row中的coordinate input
        coord = row.find('input', class_='coordinate')
        if not coord:
            continue
            
        # 從store_info div中取得門市名稱
        name = store_info.find('h4').text.strip() if store_info.find('h4') else ''
        
        # 提取電話號碼
        phone = extract_phone(store_info)
        
        # 提取其他資訊
        lat = coord.get('rel-store-lat', '0')
        lng = coord.get('rel-store-lng', '0')
        address = coord.get('rel-store-address', '').strip()
        opening_hours = coord.get('rel-store-date', '')
        
        # 處理經緯度
        try:
            lat = float(lat)
            lng = float(lng)
            coordinates = f"{lat},{lng}" if lat != 0 and lng != 0 else ""
        except ValueError:
            coordinates = ""
        
        # 處理營業時間
        start_time, end_time = parse_time(opening_hours)
        
        stores.append({
            '門市名稱': name,
            '電話': phone,
            '經緯度座標': coordinates,
            '地址': address,
            '營業時間': opening_hours,
            '開始時間': start_time,
            '結束時間': end_time
        })
    
    return stores

def main():
    # 獲取目前資料夾中所有的HTML檔案
    all_stores = []
    for file in os.listdir('.'):
        if file.endswith('.html'):
            print(f"Processing {file}...")
            stores = process_html_file(file)
            all_stores.extend(stores)
    
    # 轉換成DataFrame並存成CSV
    df = pd.DataFrame(all_stores)
    
    # 過濾掉沒有名稱的記錄
    df = df[df['門市名稱'].str.len() > 0]
    
    # 儲存CSV檔案，使用utf-8-sig編碼以正確顯示中文
    df.to_csv('路易莎門市總表.csv', index=False, encoding='utf-8-sig')
    print(f"已處理完成，共整理了 {len(df)} 間門市資訊")
    print("資料已儲存至 '路易莎門市總表.csv'")

if __name__ == "__main__":
    main()
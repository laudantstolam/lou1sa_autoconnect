import csv
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def get_coordinates(address, api_key):
    # Google Maps Geocoding API 的 URL
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
    
    # 發送請求到 API
    response = requests.get(url)
    
    # 解析回應
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'OK':
            # 提取經緯度
            lat = result['results'][0]['geometry']['location']['lat']
            lng = result['results'][0]['geometry']['location']['lng']
            return lat, lng
        else:
            print(f"Error: Unable to geocode the address: {address}")
    else:
        print(f"Error: Unable to connect to the API for address: {address}")
    return None, None

def update_csv_with_latlng(input_csv, output_csv, api_key):
    updated_rows = []
    
    # read csv
    with open(input_csv, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        updated_rows.append(header)
        
        for row in reader:
            store_name, phone, lat_lng, address, hours, start_time, end_time = row
            
            # check null
            if lat_lng == "" or lat_lng == "None" or lat_lng == "0.00,0.00":
                print(f"Missing coordinates for: {store_name} at {address}")
                
                # Geocoding API
                lat, lng = get_coordinates(address, api_key)
                
                if lat and lng:
                    lat_lng = f"{lat},{lng}"
                    print(f"Updated coordinates: {lat_lng}")
                else:
                    print(f"Could not update coordinates for: {store_name}")
            
            # update
            updated_rows.append([store_name, phone, lat_lng, address, hours, start_time, end_time])
    
    # file write
    with open(output_csv, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(updated_rows)

# ----------------------------------------
input_csv = 'query_data/01_collect.csv' 
output_csv = 'query_data/02_updated.csv'
api_key = os.getenv('GOOGLE_API_KEY')  # 從 .env 文件中讀取 API 密鑰
update_csv_with_latlng(input_csv, output_csv, api_key)

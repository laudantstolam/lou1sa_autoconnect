import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

COUNTIES = [
    "基隆市", "台北市", "新北市", "宜蘭縣",
    "新竹市", "新竹縣", "桃園市", "苗栗縣",
    "台中市", "彰化縣", "南投縣", "嘉義市",
    "嘉義縣", "雲林縣", "台南市", "高雄市",
    "屏東縣", "台東縣", "花蓮縣", "金門縣",
    "連江縣", "澎湖縣",
]

ENDPOINT = "https://www.louisacoffee.co/visit_result"
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.louisacoffee.co/visit",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
}

TIME_PATTERN = re.compile(r"(\d{1,2}:\d{2})\s*[-~～]\s*(\d{1,2}:\d{2})")


def parse_time(time_str: str):
    m = TIME_PATTERN.search(time_str)
    if m:
        return m.group(1), m.group(2)
    return "", ""


def fetch_county(session: requests.Session, county: str) -> str:
    resp = session.post(ENDPOINT, headers=HEADERS, data={"data[county]": county}, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_html(html: str, county: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    stores = []

    for row in soup.find_all("div", class_="row"):
        store_info = row.find("div", class_="store_info")
        coord = row.find("input", class_="coordinate")
        if not store_info or not coord:
            continue

        name_tag = store_info.find("h4")
        name = name_tag.text.strip() if name_tag else ""
        if not name:
            continue

        # Phone
        phone_tag = store_info.find("p", string=lambda t: t and "電話" in t)
        phone = ""
        if phone_tag:
            phone = phone_tag.text.replace("電話/", "").strip()

        # Coordinates & address from hidden input
        lat_str = coord.get("rel-store-lat", "0")
        lng_str = coord.get("rel-store-lng", "0")
        address = coord.get("rel-store-address", "").strip()
        hours_raw = coord.get("rel-store-date", "")

        try:
            lat = float(lat_str)
            lng = float(lng_str)
            coordinates = f"{lat},{lng}" if lat != 0 and lng != 0 else ""
        except ValueError:
            coordinates = ""

        start_time, end_time = parse_time(hours_raw)

        stores.append({
            "縣市": county,
            "門市名稱": name,
            "電話": phone,
            "經緯度座標": coordinates,
            "地址": address,
            "營業時間": hours_raw,
            "開始時間": start_time,
            "結束時間": end_time,
        })

    return stores


def main():
    all_stores = []
    session = requests.Session()

    for county in COUNTIES:
        print(f"Fetching {county}...", end=" ", flush=True)
        try:
            html = fetch_county(session, county)
            stores = parse_html(html, county)
            print(f"{len(stores)} stores")
            all_stores.extend(stores)
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(0.5)  # be polite

    df = pd.DataFrame(all_stores)
    df = df[df["門市名稱"].str.len() > 0]
    df = df.drop_duplicates(subset=["門市名稱", "地址"])

    out_path = "data.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nDone! {len(df)} stores saved to {out_path}")


if __name__ == "__main__":
    main()

import urllib.request
import json
import math
from datetime import datetime, timedelta

def dfs_xy_conv(lat, lon):
    RE = 6371.00877; GRID = 5.0; SLAT1 = 30.0; SLAT2 = 60.0; OLON = 126.0; OLAT = 38.0; XO = 43; YO = 136
    DEGRAD = math.pi / 180.0
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD; slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD; olat = OLAT * DEGRAD
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5))
    sf = math.pow(math.tan(math.pi * 0.25 + slat1 * 0.5), sn) * math.cos(slat1) / sn
    ro = re * sf / math.pow(math.tan(math.pi * 0.25 + olat * 0.5), sn)
    ra = re * sf / math.pow(math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5), sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi: theta -= 2.0 * math.pi
    if theta < -math.pi: theta += 2.0 * math.pi
    theta *= sn
    x = int(ra * math.sin(theta) + XO + 1.5)
    y = int(ro - ra * math.cos(theta) + YO + 1.5)
    return x, y

PUB_KEY = "9472c3d001c457d2606f4f782ec0f2984071afe67bc67578ea5d5b7512b53473"

def fetch_data(url):
    try:
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req, timeout=10)
        return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return None

def main():
    try:
        with open('stations.json', 'r', encoding='utf-8') as f:
            stations = json.load(f)
    except FileNotFoundError:
        print("stations.json 파일을 찾을 수 없습니다.")
        return

    unique_grids = set()
    for s in stations:
        nx, ny = dfs_xy_conv(s['lat'], s['lon'])
        unique_grids.add((nx, ny))

    now = datetime.now()
    if now.minute < 45:
        now -= timedelta(hours=1)
    
    b_date = now.strftime('%Y%m%d')
    ncst_time = now.strftime('%H00')
    fcst_time = now.strftime('%H30')

    weather_data = {}

    for nx, ny in unique_grids:
        grid_key = f"{nx}_{ny}"
        print(f"Fetching {grid_key}...")
        ncst_url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?pageNo=1&numOfRows=10&dataType=JSON&base_date={b_date}&base_time={ncst_time}&nx={nx}&ny={ny}&serviceKey={PUB_KEY}"
        fcst_url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst?pageNo=1&numOfRows=50&dataType=JSON&base_date={b_date}&base_time={fcst_time}&nx={nx}&ny={ny}&serviceKey={PUB_KEY}"
        
        ncst_data = fetch_data(ncst_url)
        fcst_data = fetch_data(fcst_url)
        
        weather_data[grid_key] = {
            "ncst": ncst_data,
            "fcst": fcst_data
        }

    with open('weather_data.json', 'w', encoding='utf-8') as f:
        json.dump(weather_data, f, ensure_ascii=False)
    print("Successfully updated weather_data.json!")

if __name__ == '__main__':
    main()

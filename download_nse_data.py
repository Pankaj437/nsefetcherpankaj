import requests
import pandas as pd
from datetime import datetime

symbol = 'NIFTY'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com",
    "Connection": "keep-alive",
}

session = requests.Session()
session.headers.update(headers)
session.get("https://www.nseindia.com", timeout=10)

url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
response = session.get(url, timeout=10)

if response.status_code == 200:
    data = response.json()
    records = data['records']['data']
    rows = []

    for item in records:
        ce = item.get('CE', {})
        pe = item.get('PE', {})
        strike_price = item.get('strikePrice')

        row = {
            'strikePrice': strike_price,
            'CE_OI': ce.get('openInterest'),
            'CE_Chg_OI': ce.get('changeinOpenInterest'),
            'CE_Volume': ce.get('totalTradedVolume'),
            'PE_OI': pe.get('openInterest'),
            'PE_Chg_OI': pe.get('changeinOpenInterest'),
            'PE_Volume': pe.get('totalTradedVolume'),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    df.to_csv(f"option_chain_{symbol}_{timestamp}.csv", index=False)
    print("✅ File saved")
else:
    print(f"❌ Error {response.status_code}")

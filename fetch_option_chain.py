import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

symbol = 'NIFTY'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com"
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
        rows.append([
            item.get('strikePrice'),
            ce.get('openInterest'),
            ce.get('changeinOpenInterest'),
            ce.get('totalTradedVolume'),
            pe.get('openInterest'),
            pe.get('changeinOpenInterest'),
            pe.get('totalTradedVolume'),
        ])
else:
    raise Exception("Failed to fetch NSE data")

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("OptionChainData").sheet1  # Make sure this Google Sheet exists

sheet.clear()
sheet.append_row(["strikePrice", "CE_OI", "CE_Chg_OI", "CE_Volume", "PE_OI", "PE_Chg_OI", "PE_Volume"])
for row in rows:
    sheet.append_row(row)

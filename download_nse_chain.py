import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import calendar

# Nifty index symbols and their names
NIFTY_INDICES = {
    "NIFTY": "Nifty 50",
    "BANKNIFTY": "Nifty Bank",
    "FINNIFTY": "Nifty Financial Services",
    "MIDCPNIFTY": "Nifty Midcap Select",
    "NIFTYNXT50": "Nifty Next 50"
}

def get_next_month_expiry():
    """Return the last Thursday of the next month as expiry date (in format: DD-MMM-YYYY)."""
    today = datetime.today()
    # First day of next month
    if today.month == 12:
        next_month = datetime(today.year + 1, 1, 1)
    else:
        next_month = datetime(today.year, today.month + 1, 1)

    # Find all Thursdays in next month
    last_day = calendar.monthrange(next_month.year, next_month.month)[1]
    thursdays = [day for day in range(1, last_day + 1)
                 if datetime(next_month.year, next_month.month, day).weekday() == 3]

    last_thursday = thursdays[-1]
    expiry_date = datetime(next_month.year, next_month.month, last_thursday)
    return expiry_date.strftime("%d-%b-%Y").upper()

async def fetch_option_chain(page, symbol, expiry_date):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}&expiryDate={expiry_date}"
    try:
        response = await page.evaluate("""
            async (url) => {
                const res = await fetch(url, {
                    method: "GET",
                    headers: {
                        "Accept": "application/json, text/javascript, */*; q=0.01",
                        "User-Agent": navigator.userAgent,
                        "Referer": "https://www.nseindia.com/option-chain"
                    },
                    credentials: "include"
                });
                const text = await res.text();
                try {
                    return JSON.parse(text);
                } catch (e) {
                    console.error("❌ JSON parse error:", text);
                    throw e;
                }
            }
        """, url)

        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        file_name = f"{symbol.lower()}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4)
        print(f"✅ {symbol} data saved to {file_name}")
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {str(e)}")

async def fetch_all_indices():
    expiry_date = get_next_month_expiry()
    print(f"📅 Using expiry date: {expiry_date}")

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto("https://www.nseindia.com", timeout=30000)
            await page.wait_for_load_state("networkidle")
        except PlaywrightTimeoutError:
            print("⚠️ Homepage load timeout—continuing anyway...")

        for symbol in NIFTY_INDICES:
            await fetch_option_chain(page, symbol, expiry_date)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_all_indices())

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Define all Nifty indices you want to fetch
NIFTY_INDICES = {
    "NIFTY": "Nifty 50",
    "BANKNIFTY": "Nifty Bank",
    "FINNIFTY": "Nifty Financial Services",
    "MIDCPNIFTY": "Nifty Midcap Select",
    "NIFTYNXT50": "Nifty Next 50"
}

EXPIRY_DATE = "29-MAY-2025"

async def fetch_option_chain(page, symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}&expiryDate={EXPIRY_DATE}"
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
        file_name = f"option_chain_{symbol}_{date_str}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4)
        print(f"✅ {symbol} data saved to {file_name}")
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {str(e)}")

async def fetch_all_indices():
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
            await fetch_option_chain(page, symbol)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_all_indices())

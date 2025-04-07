import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def fetch_nse_data():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTYNXT50&expiryDate=29-MAY-2025"
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    output_file = f"option_chain_{date_str}.json"

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
            print("⚠️ Homepage timeout—continuing...")

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

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(response, f, indent=4)
            print(f"✅ Saved to {output_file}")

        except Exception as e:
            print(f"❌ Failed: {str(e)}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_nse_data())

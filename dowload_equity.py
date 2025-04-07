import asyncio
import json
import os
import pandas as pd
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def fetch_nse_data_for_symbol(symbol, expiry_date="29-MAY-2025"):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}&expiryDate={expiry_date}"

    # Define the output directory
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)  # Set to False for debugging
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Step 1: Open NSE homepage to establish session and cookies
        try:
            await page.goto("https://www.nseindia.com", timeout=30000)
            await page.wait_for_load_state("networkidle")
        except PlaywrightTimeoutError:
            print(f"❌ Homepage load timed out for {symbol}, but proceeding with API call...")

        # Step 2: Fetch option chain data
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
                        credentials: "include"  // Include cookies from the homepage visit
                    });
                    const text = await res.text();  // Get raw text for debugging
                    try {
                        return JSON.parse(text);  // Attempt to parse as JSON
                    } catch (e) {
                        console.error("Failed to parse JSON:", text);
                        throw e;  // Re-throw the error to be caught in Python
                    }
                }
            """, url)

            # Save data to a JSON file in the 'data' directory
            file_name = f"{symbol.lower()}.json"
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(response, f, indent=4)
            print(f"✅ Option chain data for {symbol} saved to {file_name}")

        except Exception as e:
            print(f"❌ Error fetching or parsing API response for {symbol}: {str(e)}")

        await browser.close()

async def fetch_nse_data(csv_file_path="equity.csv"):
    # Read the CSV file containing symbols
    try:
        df = pd.read_csv(csv_file_path)
        if "Symbol" not in df.columns:
            print("❌ Error: 'Symbol' column not found in CSV.")
            return
        symbols = df["Symbol"].tolist()  # Extract the 'Symbol' column
    except FileNotFoundError:
        print(f"❌ Error: The file '{csv_file_path}' was not found.")
        return
    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        return

    # Fetch data for each symbol one by one
    for symbol in symbols:
        print(f"Processing {symbol}...")
        await fetch_nse_data_for_symbol(symbol)
        await asyncio.sleep(1)  # Add a delay to avoid overwhelming the server

# Run the Playwright script
async def main():
    await fetch_nse_data("equity.csv")

if __name__ == "__main__":
    asyncio.run(main())

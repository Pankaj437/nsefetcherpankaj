import time
from playwright.sync_api import Playwright, sync_playwright

# List of credentials (email, password)
accounts = [
    ("goxaf26@buides.com", "sharma8092"),
    ("enormpan@gmail.com", "pankaj437"),
    ("technologysha9@gmail.com", "sharma437"),
    ("abhishr4709@gmail.com", "pankaj437"),
    ("nitrmaofficial0@gmail.com", "pankaj437"),
    ("xikad@abnovel.com", "pankaj437"),
  
]

# Dashboard sections to capture
sections = {
    "whatsappmessages": "whatsapp_data.png",   
    "sms": "sms.png",    
}

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)

    for index, (email, password) in enumerate(accounts, start=1):
        print(f"\n🔐 Logging in with Account {index}: {email}")
        context = browser.new_context()
        page = context.new_page()

        try:
            # Login
            page.goto("https://mobile-tracker-free.com/")
            page.get_by_role("link", name=" Login").click()
            page.get_by_role("textbox", name="Email").fill(email)
            page.get_by_role("textbox", name="Password").fill(password)
            time.sleep(2)
            page.get_by_role("button", name="Sign in ").click()
            page.wait_for_timeout(3000)

            # Try to close ad
            try:
                iframe = page.frame(name="aswift_5")
                if iframe:
                    close_btn = iframe.get_by_role("button", name="Close ad")
                    if close_btn:
                        close_btn.click()
            except Exception as e:
                print("Ad close failed or not present:", e)

            # Navigate and screenshot sections
            for section, base_filename in sections.items():
                try:
                    url = f"https://mobile-tracker-free.com/dashboard/{section}.php"
                    print(f"📄 Visiting {url}")
                    page.goto(url)
                    page.wait_for_timeout(3000)

                    filename = f"acc{index}_{base_filename}"
                    if page.locator("table").is_visible():
                        page.locator("table").screenshot(path=filename)
                    else:
                        page.screenshot(path=filename, full_page=True)

                    print(f"✅ Saved screenshot: {filename}")
                except Exception as e:
                    print(f"❌ Failed to capture {section} for account {index}: {e}")

        except Exception as e:
            print(f"❌ Login failed for account {index}: {e}")
        finally:
            context.close()

    browser.close()

with sync_playwright() as playwright:
    run(playwright)

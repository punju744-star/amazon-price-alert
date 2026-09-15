from playwright.sync_api import sync_playwright

url = "https://www.amazon.in/dp/B0099M2IQY"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        locale="en-IN",
    )

    page.goto(url, wait_until="domcontentloaded", timeout=60000)

    print("Final URL:", page.url)
    print("Page title:", page.title())
    print("Page length:", len(page.content()))

    print("\nPage text preview:\n")
    print(page.locator("body").inner_text()[:2000])

    browser.close()

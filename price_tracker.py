import os
import re
import requests
from bs4 import BeautifulSoup

PRODUCTS = [
    {
        "url": "https://www.amazon.in/dp/B0CG3D9F6G",
        "target": 4000,
    },
    {
        "url": "https://www.amazon.in/dp/B00A2EPT8W",
        "target": 2000,
    },
    {
        "url": "https://www.amazon.in/dp/B0099M2IQY",
        "target": 2000,
    },
]

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def get_amazon_price(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-IN,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
        allow_redirects=True,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Method 1: Amazon's normal price elements
    selectors = [
        "#corePriceDisplay_desktop_feature_div .a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-price-whole",
        "#corePrice_feature_div .a-offscreen",
        "#apex_desktop .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#priceblock_saleprice",
        ".a-price .a-offscreen",
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            text = element.get_text(" ", strip=True)
            match = re.search(r"[\d,]+(?:\.\d{1,2})?", text)

            if match:
                price = float(match.group().replace(",", ""))

                if price > 0:
                    return price

    # Method 2: meta price
    meta_selectors = [
        'meta[property="product:price:amount"]',
        'meta[itemprop="price"]',
    ]

    for selector in meta_selectors:
        element = soup.select_one(selector)

        if element and element.get("content"):
            try:
                price = float(element["content"].replace(",", ""))

                if price > 0:
                    return price
            except ValueError:
                pass

    # Method 3: JSON-LD product price
    for script in soup.find_all("script", type="application/ld+json"):
        script_text = script.get_text(strip=True)

        matches = re.findall(
            r'"price"\s*:\s*"?(?:₹\s*)?([\d,]+(?:\.\d{1,2})?)',
            script_text,
            re.IGNORECASE,
        )

        for value in matches:
            price = float(value.replace(",", ""))

            if price > 0:
                return price

    # Method 4: search visible page text
    text = soup.get_text(" ", strip=True)

    matches = re.findall(
        r"₹\s*([\d,]+(?:\.\d{1,2})?)",
        text,
    )

    prices = []

    for value in matches:
        try:
            price = float(value.replace(",", ""))

            if price > 0:
                prices.append(price)
        except ValueError:
            pass

    if prices:
        return min(prices)

    raise RuntimeError("Could not find Amazon price.")


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("Telegram secrets are missing.")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=20,
    )

    response.raise_for_status()


def main():
    alerts = []

    for product in PRODUCTS:
        url = product["url"]
        target = product["target"]

        try:
            price = get_amazon_price(url)

            print(f"Product: {url}")
            print(f"Current price: ₹{price:.2f}")
            print(f"Target price: ₹{target}")

            if price <= target:
                alerts.append(
                    f"🚨 AMAZON PRICE ALERT 🚨\n\n"
                    f"Current price: ₹{price:.2f}\n"
                    f"Target price: ₹{target}\n\n"
                    f"Buy here:\n{url}"
                )
            else:
                print("Price is above target.")

        except Exception as error:
            print(f"Error checking {url}: {error}")

    if alerts:
        send_telegram("\n\n--------------------\n\n".join(alerts))
        print("Telegram alert sent!")
    else:
        print("No products reached their target price.")


if __name__ == "__main__":
    main()

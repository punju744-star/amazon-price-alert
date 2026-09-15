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
            "Chrome/140.0 Safari/537.36"
        ),
        "Accept-Language": "en-IN,en;q=0.9",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20,
        allow_redirects=True
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    selectors = [
        "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-price-whole",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".a-price .a-offscreen",
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            text = element.get_text(strip=True)
            numbers = re.sub(r"[^\d.]", "", text)

            if numbers:
                return float(numbers)

    text = soup.get_text(" ", strip=True)

    matches = re.findall(
        r"₹\s*([\d,]+(?:\.\d{1,2})?)",
        text
    )

    prices = []

    for value in matches:
        try:
            prices.append(float(value.replace(",", "")))
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
    for product in PRODUCTS:
        url = product["url"]
        target = product["target"]

        try:
            price = get_amazon_price(url)

            print(f"{url}")
            print(f"Current price: ₹{price:.2f}")
            print(f"Target price: ₹{target}")

            if price <= target:
                message = (
                    "🚨 AMAZON PRICE ALERT 🚨\n\n"
                    f"Current price: ₹{price:.2f}\n"
                    f"Target price: ₹{target}\n\n"
                    f"Buy here:\n{url}"
                )

                send_telegram(message)

                print("Telegram alert sent!")

            else:
                print("Price is above target.")

        except Exception as error:
            print(f"Error checking {url}: {error}")


if __name__ == "__main__":
    main()

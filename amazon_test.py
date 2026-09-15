import requests

url = "https://www.amazon.in/dp/B0099M2IQY"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

response = requests.get(
    url,
    headers=headers,
    timeout=30,
    allow_redirects=True,
)

print("Status:", response.status_code)
print("Final URL:", response.url)
print("Page length:", len(response.text))

print("\nFirst 1000 characters:\n")
print(response.text[:1000])

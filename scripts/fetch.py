import requests

url = "https://example.com"
response = requests.get(url)

with open("example.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Downloaded example.com successfully.")

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random

BASE = "https://ru.wikipedia.org"

def get_random_page():
    url = "https://ru.wikipedia.org/api/rest_v1/page/random/summary"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(url, headers=headers, timeout=10)

    if resp.status_code != 200:
        raise Exception("Request failed:", resp.status_code)

    try:
        data = resp.json()
    except:
        print("Response was not JSON:")
        print(resp.text[:200])
        raise

    return data["content_urls"]["desktop"]["page"]

def get_random_link(soup):
    links = list(set(
        a["href"]
        for a in soup.find_all("a", href=True)
        if a["href"].startswith("/wiki/") and ":" not in a["href"]
    ))

    if not links:
        return None

    return random.choice(links)


current_page = get_random_page()

visited = []

headers = {"User-Agent": "Mozilla/5.0"}

for i in range(3):
    response = requests.get(current_page, headers=headers)

    if response.status_code != 200:
        print("Failed to load:", current_page)
        break

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1")
    if not title_tag:
        print("No title found:", current_page)
        break

    title = title_tag.text.strip()

    print(title, "->", current_page)
    visited.append((title, current_page))

    link = get_random_link(soup)

    if not link:
        print("No valid links found")
        break

    current_page = urljoin(BASE, link)

with open("links.txt", "w", encoding="utf-8") as f:
    for t, u in visited:
        f.write(f"{t} -> {u}\n")
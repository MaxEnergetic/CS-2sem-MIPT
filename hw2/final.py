import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from collections import deque
import time

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import random


BASE = "https://en.wikipedia.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
def get_random_page():
    url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"

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

target='Law of large numbers'
target_link = "https://en.wikipedia.org/wiki/Law_of_large_numbers"
max_steps = 30       
n_runs = 50         
sleep = 0.5     

def run_walk(max_steps=max_steps):
    current_page = get_random_page()

    for step in range(max_steps):
        try:
            response = requests.get(current_page, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("h1")
        if not title_tag:
            return None

        title = title_tag.text.strip()

        print(f"Step {step}: {title}")
        link = current_page.split("#")[0]

    
        if title == target or link == target_link:
            return step

        link = get_random_link(soup)
        if not link:
            return None

        current_page = BASE + link

        time.sleep(sleep)

    return None  


def experiment(n_runs=n_runs):
    results = []
    failures = 0

    for i in range(n_runs):
        print(f"\n=== Забег {i + 1} ===")

        steps = run_walk()

        if steps is not None:
            results.append(steps)
            print(f"Дошли до цели за {steps}")
        else:
            failures += 1
            print("Споткнулись")

    return results, failures


def plot_results(results):
    if not results:
        print("Мы не дошли :(")
        return

    plt.hist(results, bins=10)
    plt.xlabel("Количество шагов")
    plt.ylabel("Частота")
    plt.title("Случайная прогулка(блуждание) до закона больших чисел")
    plt.show()




results, failures = experiment()

print("\n=== Итог ===")
print("Дотопали столько раз:", len(results))
print("Упали:", failures)

if results:
    print("В среднем топали:", sum(results) / len(results))

plot_results(results)
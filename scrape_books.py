# scrape_books.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

BASE_URL = "http://books.toscrape.com/"

def fetch_book_titles(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    books = soup.select(".product_pod h3 a")
    return [book["title"] for book in books]

def save_to_csv(titles, filepath):
    df = pd.DataFrame(titles, columns=["Book Title"])
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"✅ Saved {len(titles)} titles to {filepath}")

if __name__ == "__main__":
    print("🔍 Scraping book titles from books.toscrape.com...")
    titles = fetch_book_titles(BASE_URL)
    save_to_csv(titles, "data/books.csv")
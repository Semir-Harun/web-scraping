"""scrape_products.py

Simple scraper for books.toscrape.com that demonstrates requests + BeautifulSoup + pandas.

Usage:
    python scrape_products.py --pages 2

This script scrapes the given number of pages (default 2) and writes data to data/products.csv.
"""
import argparse
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


def parse_rating(tag):
    """Extract human-readable rating from the star-rating class."""
    classes = tag.get('class', [])
    # e.g., ['star-rating', 'Three'] -> return 'Three'
    for c in classes:
        if c.lower() in ('one', 'two', 'three', 'four', 'five'):
            # normalize capitalization
            return c.capitalize()
    return ''


def scrape_page(session, url):
    r = session.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    items = []

    for article in soup.select('article.product_pod'):
        h3 = article.find('h3')
        a = h3.find('a')
        title = a.get('title') or a.get_text(strip=True)
        rel_link = a.get('href')
        product_page = urljoin(url, rel_link)

        price_tag = article.select_one('p.price_color')
        price = price_tag.get_text(strip=True) if price_tag else ''

        avail_tag = article.select_one('p.instock.availability')
        availability = avail_tag.get_text(strip=True) if avail_tag else ''

        rating_tag = article.select_one('p.star-rating')
        rating = parse_rating(rating_tag) if rating_tag else ''

        items.append({
            'title': title,
            'price': price,
            'availability': availability,
            'rating': rating,
            'product_page': product_page,
        })

    return items


def main(pages: int, out_path: str):
    base = 'https://books.toscrape.com/'
    session = requests.Session()
    session.headers.update({'User-Agent': 'web-scraping-example/1.0'})

    all_items = []
    for p in range(1, pages + 1):
        if p == 1:
            url = base
        else:
            url = urljoin(base, f'catalogue/page-{p}.html')

        print(f"Scraping page {p}: {url}")
        try:
            items = scrape_page(session, url)
        except Exception as e:
            print(f"  Failed to scrape {url}: {e}")
            break

        print(f"  Found {len(items)} items")
        all_items.extend(items)
        # polite short pause
        time.sleep(1.0)

    if not all_items:
        print("No items scraped.")
        return

    df = pd.DataFrame(all_items)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
    print(df.head().to_string(index=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape books.toscrape.com and save products to CSV')
    parser.add_argument('--pages', type=int, default=2, help='Number of pages to scrape (default: 2)')
    parser.add_argument('--out', default='data/products.csv', help='Output CSV path (default: data/products.csv)')
    args = parser.parse_args()

    main(args.pages, args.out)

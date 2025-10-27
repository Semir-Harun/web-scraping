# web-scraping

This repository contains a small, professional example project for web scraping.

What you'll find here
- A simple, reproducible scraper `scrape_products.py` that scrapes product data from books.toscrape.com (a site designed for scraping practice).
- A `requirements.txt` for Python dependencies.
- Example output in `data/products.csv` produced by scraping the first 1–2 pages.

Project structure

web-scraping/
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── scrape_products.py   # Example scraper (requests + BeautifulSoup + pandas)
├── data/
│   └── products.csv     # Sample scraped data

Quick summary

This example demonstrates a small, maintainable scraping script:

- Uses `requests` for HTTP requests.
- Parses HTML with `BeautifulSoup` (parser: lxml).
- Aggregates results in a pandas DataFrame and writes CSV to `data/products.csv`.
- Default target: https://books.toscrape.com — a legal practice site for scraping.

How to run

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Run the scraper (default scrapes 2 pages):

```powershell
python scrape_products.py --pages 2
```

3. Output will be written to `data/products.csv` and a short preview printed to the console.

Sample output (first rows)

title,price,availability,rating,product_page
"A Light in the Attic","£51.77","In stock (22 available)",Three,https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
"Tipping the Velvet","£53.74","In stock (20 available)",One,https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html

Notes

- This project is intentionally tiny and educational. For larger projects consider using scraping frameworks (Scrapy), robust retry/backoff, rotating proxies, and respectful rate limiting. Always check and respect a site's robots.txt and terms of service.

License & attribution

This repository is a personal/educational example.

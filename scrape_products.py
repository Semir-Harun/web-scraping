"""scrape_products.py

Enhanced scraper for books.toscrape.com with modular design, logging, and robust error handling.

Usage:
    python scrape_products.py --pages 2 --verbose

This script scrapes the given number of pages (default 2) and writes data to data/products.csv.
"""
import argparse
import logging
import os
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag


# Configure logging
def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def parse_rating(tag: Optional[Tag]) -> str:
    """Extract human-readable rating from the star-rating class."""
    if not tag:
        return ''
    
    classes = tag.get('class', [])
    # e.g., ['star-rating', 'Three'] -> return 'Three'
    for c in classes:
        if c.lower() in ('one', 'two', 'three', 'four', 'five'):
            # normalize capitalization
            return c.capitalize()
    return ''


def fetch_page(session: requests.Session, url: str) -> BeautifulSoup:
    """Fetch a single page and return parsed BeautifulSoup object."""
    logging.debug(f"Fetching URL: {url}")
    
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        logging.debug(f"Successfully fetched {url} ({response.status_code})")
        return BeautifulSoup(response.text, 'lxml')
    except requests.exceptions.Timeout:
        logging.error(f"Timeout while fetching {url}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {url}: {e}")
        raise


def parse_items(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    """Parse book items from a BeautifulSoup page object."""
    items = []
    articles = soup.select('article.product_pod')
    
    logging.debug(f"Found {len(articles)} articles on page")
    
    for i, article in enumerate(articles, 1):
        try:
            # Extract title and product URL
            h3 = article.find('h3')
            if not h3:
                logging.warning(f"Article {i}: No h3 tag found, skipping")
                continue
                
            a = h3.find('a')
            if not a:
                logging.warning(f"Article {i}: No anchor tag found, skipping")
                continue
                
            title = a.get('title') or a.get_text(strip=True)
            rel_link = a.get('href')
            product_page = urljoin(base_url, rel_link) if rel_link else ''

            # Extract price
            price_tag = article.select_one('p.price_color')
            price = price_tag.get_text(strip=True) if price_tag else 'N/A'

            # Extract availability
            avail_tag = article.select_one('p.instock.availability')
            availability = avail_tag.get_text(strip=True) if avail_tag else 'N/A'

            # Extract rating
            rating_tag = article.select_one('p.star-rating')
            rating = parse_rating(rating_tag)

            item = {
                'title': title,
                'price': price,
                'availability': availability,
                'rating': rating,
                'product_page': product_page,
            }
            
            items.append(item)
            logging.debug(f"Article {i}: Parsed '{title[:30]}...' - {price} - {rating} stars")
            
        except Exception as e:
            logging.warning(f"Article {i}: Failed to parse - {e}")
            continue

    logging.info(f"Successfully parsed {len(items)} items from page")
    return items


def get_page_url(base_url: str, page_num: int) -> str:
    """Generate URL for a specific page number."""
    if page_num == 1:
        return base_url
    else:
        return urljoin(base_url, f'catalogue/page-{page_num}.html')


def scrape_multiple_pages(base_url: str, pages: int, delay: float = 1.0) -> List[Dict[str, str]]:
    """Scrape multiple pages and return combined results."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'web-scraping-example/2.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    })

    all_items = []
    successful_pages = 0
    
    for page_num in range(1, pages + 1):
        url = get_page_url(base_url, page_num)
        logging.info(f"Scraping page {page_num}/{pages}: {url}")
        
        try:
            soup = fetch_page(session, url)
            items = parse_items(soup, url)
            
            if not items:
                logging.warning(f"Page {page_num}: No items found, stopping pagination")
                break
                
            all_items.extend(items)
            successful_pages += 1
            logging.info(f"Page {page_num}: Added {len(items)} items (total: {len(all_items)})")
            
            # Respectful delay between requests
            if page_num < pages:
                logging.debug(f"Waiting {delay}s before next request...")
                time.sleep(delay)
                
        except Exception as e:
            logging.error(f"Page {page_num}: Failed to scrape - {e}")
            continue

    logging.info(f"Scraping completed: {successful_pages}/{pages} pages successful, {len(all_items)} total items")
    return all_items


def save_data(items: List[Dict[str, str]], output_path: str, show_preview: bool = True) -> None:
    """Save scraped data to CSV file."""
    if not items:
        logging.warning("No items to save")
        return

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create DataFrame and save
    df = pd.DataFrame(items)
    df.to_csv(output_path, index=False)
    
    logging.info(f"Saved {len(df)} rows to {output_path}")
    
    # Show preview
    if show_preview:
        print(f"\n📊 Data Preview ({len(df)} rows):")
        print("=" * 50)
        print(df.head().to_string(index=False))
        
        # Basic statistics
        print(f"\n📈 Quick Statistics:")
        print(f"  Total books: {len(df)}")
        if 'rating' in df.columns:
            rating_counts = df['rating'].value_counts()
            print(f"  Most common rating: {rating_counts.index[0] if not rating_counts.empty else 'N/A'}")
        if 'price' in df.columns:
            price_range = df['price'].nunique()
            print(f"  Unique prices: {price_range}")


def main():
    """Main function to orchestrate the scraping process."""
    parser = argparse.ArgumentParser(
        description='Enhanced scraper for books.toscrape.com with logging and robust error handling'
    )
    parser.add_argument('--pages', type=int, default=2, 
                       help='Number of pages to scrape (default: 2)')
    parser.add_argument('--out', default='data/products.csv', 
                       help='Output CSV path (default: data/products.csv)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose debug logging')
    parser.add_argument('--no-preview', action='store_true',
                       help='Skip showing data preview')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Configuration
    base_url = 'https://books.toscrape.com/'
    
    logging.info("Starting web scraping process")
    logging.info(f"Target: {base_url}")
    logging.info(f"Pages to scrape: {args.pages}")
    logging.info(f"Output file: {args.out}")
    logging.info(f"Request delay: {args.delay}s")
    
    try:
        # Scrape data
        items = scrape_multiple_pages(base_url, args.pages, args.delay)
        
        if not items:
            logging.error("No data scraped. Exiting.")
            return 1
            
        # Save data
        save_data(items, args.out, show_preview=not args.no_preview)
        
        logging.info("Scraping process completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
        return 1
    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        return 1


if __name__ == '__main__':
    exit(main())

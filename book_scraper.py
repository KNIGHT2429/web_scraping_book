"""
Polite Web Scraper 
This shows the three good habits of ethical scraping:

  1. SLOW DOWN  -> wait a moment between requests (time.sleep)
  2. CHECK RULES -> read robots.txt to see what the site allows
  3. IDENTIFY YOURSELF -> send a clear User-Agent header

These habits keep you from overloading a server or getting blocked.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time                              # for adding delays
import urllib.robotparser                # for reading robots.txt


BASE_URL = "https://books.toscrape.com"

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

# A User-Agent tells the website who is visiting. Being honest is polite.
HEADERS = {
    "User-Agent": "LearningScraper/1.0 (practice project)"
}

# How long to wait between each page request, in seconds.
DELAY_SECONDS = 1


def is_allowed(url):
    """HABIT 2: Check robots.txt to see if scraping this URL is allowed."""
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{BASE_URL}/robots.txt")
    try:
        rp.read()                              # download and read the rules
    except Exception:
        # If robots.txt can't be read, be cautious but proceed for practice sites
        print("Could not read robots.txt - proceeding carefully.")
        return True
    # "*" means "any scraper/bot". Returns True if we're allowed to fetch.
    return rp.can_fetch("*", url)


def scrape_books(pages_to_scrape=3):
    """Scrape several pages politely and return a list of book data."""
    all_books = []

    for page_number in range(1, pages_to_scrape + 1):
        url = f"{BASE_URL}/catalogue/page-{page_number}.html"

        # HABIT 2: ask permission before scraping this page
        if not is_allowed(url):
            print(f"robots.txt does not allow scraping {url} - skipping.")
            continue

        print(f"Scraping page {page_number} ...")

        # HABIT 3: send our honest User-Agent with the request
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            # Don't crash if one page fails - report it and move on
            print(f"  Could not fetch page {page_number}: {error}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").text.strip()
            rating_word = book.find("p", class_="star-rating")["class"][1]
            rating = RATING_WORDS.get(rating_word, 0)
            availability = book.find("p", class_="instock availability").text.strip()

            all_books.append({
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
            })

        # HABIT 1: wait politely before requesting the next page
        print(f"  Waiting {DELAY_SECONDS} second(s) before the next page...")
        time.sleep(DELAY_SECONDS)

    return all_books


def save_to_csv(books, filename="books.csv"):
    """Save the list of books into a CSV file."""
    fieldnames = ["title", "price", "rating", "availability"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)
    print(f"\nSaved {len(books)} books to '{filename}'")


if __name__ == "__main__":
    books = scrape_books(pages_to_scrape=3)
    save_to_csv(books)

    print("\nFirst few books found:")
    for book in books[:5]:
        print(f"  {book['rating']}star  {book['price']:>8}  {book['title']}")

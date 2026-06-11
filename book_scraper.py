"""
Simple Web Scraper 
This script visits books.toscrape.com , collects information about books, and saves it to a CSV file.

What it collects for each book:
  - Title
  - Price
  - Rating (how many stars)
  - Availability (in stock or not)
"""

import requests                  # used to download web pages
from bs4 import BeautifulSoup     # used to read/understand the HTML
import csv                        # used to save data into a CSV file


# Convert the word rating ("Three") into a number (3) so it's easier to use
RATING_WORDS = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}


def scrape_books(pages_to_scrape=3):
    """Scrape several pages of books and return a list of book data."""
    all_books = []   # we will store every book we find in this list

    # The website splits books across many pages.
    # Page URLs look like: .../catalogue/page-1.html, page-2.html, etc.
    for page_number in range(1, pages_to_scrape + 1):
        url = f"https://books.toscrape.com/catalogue/page-{page_number}.html"
        print(f"Scraping page {page_number} ...")

        # STEP 1: Download the page
        response = requests.get(url)
        response.raise_for_status()   # stop with an error if download failed

        # STEP 2: Parse the HTML so we can search inside it
        soup = BeautifulSoup(response.text, "html.parser")

        # STEP 3: Find every book on the page.
        # On this site each book sits inside an <article class="product_pod">
        books = soup.find_all("article", class_="product_pod")

        # STEP 4: Pull out the details from each book
        for book in books:
            # Title is stored in the "title" attribute of the <a> tag
            title = book.h3.a["title"]

            # Price is inside a <p class="price_color">, e.g. "£51.77"
            price = book.find("p", class_="price_color").text.strip()

            # Rating is stored as a CSS class, e.g. class="star-rating Three"
            rating_word = book.find("p", class_="star-rating")["class"][1]
            rating = RATING_WORDS.get(rating_word, 0)

            # Availability text, e.g. "In stock"
            availability = book.find("p", class_="instock availability").text.strip()

            # Save this book's info as a dictionary
            all_books.append({
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
            })

    return all_books


def save_to_csv(books, filename="books.csv"):
    """Save the list of books into a CSV file."""
    # The column names come from the dictionary keys
    fieldnames = ["title", "price", "rating", "availability"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()          # write the column titles first
        writer.writerows(books)       # then write every book row

    print(f"\nSaved {len(books)} books to '{filename}'")


# This part runs when you start the script
if __name__ == "__main__":
    books = scrape_books(pages_to_scrape=3)   # change the number to scrape more
    save_to_csv(books)

    # Show the first 5 books in the terminal so you can see it worked
    print("\nFirst few books found:")
    for book in books[:5]:
        print(f"  {book['rating']}★  {book['price']:>8}  {book['title']}")
"""
Module for monitoring and scraping properties from the Rightmove website in the UK.

It leverages aiohttp for asynchronous HTTP requests, BeautifulSoup for HTML parsing,
and sqlite3 to store property data in a local database.
The module includes functionalities for User-Agent rotation, exponential backoff retries,
and robust logging.
"""

# Standard library imports
import random
import asyncio
import logging
import sqlite3
import csv
from datetime import datetime

# Third-party library imports
import aiohttp
from bs4 import BeautifulSoup

# Base URL for scraping. The `{}` is a placeholder for the pagination index.
BASE_URL = "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&index={}"

# List of real and updated User-Agents to simulate different browsers and avoid detection.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4; rv:115.0) Gecko/20100101 Firefox/115.0",
]

# Configure the logging system. Messages will be written to 'output/log_scrape.log'.
logging.basicConfig(
    filename="output/log_scrape.log",  # Log file name
    level=logging.INFO,  # Minimum level of messages to log (INFO, WARNING, ERROR, DEBUG)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
)

# Limits the maximum number of concurrent HTTP requests to avoid overwhelming the server.
semaphore = asyncio.Semaphore(5)


async def fetch(
    session: aiohttp.ClientSession, url: str, retries: int = 3
) -> str | None:
    """
    Performs an HTTP GET request to a given URL, handling User-Agent rotation, retries, and backoff.
    Also checks for suspicious responses (e.g., captcha or blocks).

    Args:
        session (aiohttp.ClientSession): The aiohttp client session for HTTP requests.
        url (str): The URL from which to download content.
        retries (int): Maximum number of retries in case of failure.

    Returns:
        str | None: The HTML content of the page as a string if the request is successful,
                    otherwise None in case of errors or blocks.
    """
    async with semaphore:  # Acquire the semaphore before making the request
        for attempt in range(1, retries + 1):
            user_agent = random.choice(USER_AGENTS)  # Choose a random User-Agent
            headers = {"User-Agent": user_agent}
            try:
                logging.info(
                    f"[Attempt {attempt}] Scraping URL: {url} with User-Agent: {user_agent}"
                )
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        # Basic check to detect blocks like captcha or too many requests
                        if "captcha" in text.lower() or "blocked" in text.lower():
                            logging.warning(f"Captcha/Block detected on {url}")
                            return None
                        return text
                    elif response.status == 429:  # "Too Many Requests" status code
                        logging.warning(f"429 Too Many Requests on {url}")
                    else:
                        logging.warning(
                            f"HTTP {response.status} received for URL: {url}"
                        )
            except asyncio.TimeoutError:
                logging.warning(f"Timeout on attempt {attempt} for URL: {url}")
            except aiohttp.ClientError as e:
                logging.error(f"Client error on attempt {attempt} for URL: {url}: {e}")
            except Exception as e:
                logging.error(
                    f"Unexpected error on attempt {attempt} for URL: {url}: {e}"
                )

            # Exponential backoff with random jitter to avoid predictable request patterns
            wait_time = (2**attempt) + random.uniform(0, 1)
            logging.info(f"Waiting {wait_time:.2f} seconds before retry...")
            await asyncio.sleep(wait_time)

        logging.error(f"Failed to retrieve URL after {retries} attempts: {url}")
        return None


def parse_listings(html: str) -> list[dict]:
    """
    Parses the HTML content to extract property data.

    Args:
        html (str): The HTML content of the page to parse.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a property
                    with keys like 'price', 'address', 'description', 'bedrooms', 'link'.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Selects all divs that represent a single property card using a class attribute starting with "PropertyCard_propertyCardContainer__"
    listings = soup.select('div[class^="PropertyCard_propertyCardContainer__"]')
    data = []

    for card in listings:
        price = None
        address = None
        description = None
        bedrooms = None
        full_link = None

        # Safe data extraction using try-except blocks to handle potentially missing elements
        try:
            price = card.select_one("div.PropertyPrice_price__VL65t").text.strip()
        except AttributeError:
            logging.debug("Price element not found for a card. Setting to None.")
        try:
            address = card.select_one(
                "address.PropertyAddress_address__LYRPq"
            ).text.strip()
        except AttributeError:
            logging.debug("Address element not found for a card. Setting to None.")
        try:
            description = card.select_one(
                "p.PropertyCardSummary_summary__oIv57"
            ).text.strip()
        except AttributeError:
            logging.debug("Description element not found for a card. Setting to None.")
        try:
            bedrooms = card.select_one(
                "span.PropertyInformation_bedroomsCount___2b5R"
            ).text.strip()
        except AttributeError:
            logging.debug("Bedrooms element not found for a card. Setting to None.")
        try:
            link = card.select_one("a.propertyCard-link")["href"]
            full_link = "https://www.rightmove.co.uk" + link
        except (AttributeError, TypeError, KeyError):
            logging.debug(
                "Link element not found or invalid for a card. Setting to None."
            )

        data.append(
            {
                "price": price,
                "address": address,
                "description": description,
                "bedrooms": bedrooms,
                "link": full_link,
            }
        )

    return data


async def scrape_page(session: aiohttp.ClientSession, index: int) -> list[dict]:
    """
    Scrapes a single page from the Rightmove website.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        index (int): The starting index for properties on the page (e.g., 0, 24, 48...).

    Returns:
        list[dict]: A list of dictionaries containing the found property data.
    """
    url = BASE_URL.format(index)
    html = await fetch(session, url)
    # Add a random delay to avoid overwhelming the server and reduce the risk of being blocked
    await asyncio.sleep(random.uniform(1, 3))
    if html:
        return parse_listings(html)
    else:
        return []


async def scrape_and_save_properties(pages: int = 10):
    """
    Main function that executes scraping of all requested pages in parallel.
    Connects to the database, creates the table if it doesn't exist, and inserts data preventing duplicates.
    Finally, it exports the data to a CSV file.

    Args:
        pages (int): The number of pages to scrape.
    """
    # Connect to SQLite DB. The path is updated for the new structure.
    # This path assumes the script is run from a location where 'data/property_listings.db' is accessible.
    db_path = "data/property_listings.db"  # Database file name updated as agreed
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQLite DB setup with a UNIQUE constraint on the 'link' column to prevent duplicate entries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        price TEXT,
        address TEXT,
        description TEXT,
        bedrooms TEXT,
        link TEXT UNIQUE,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    async with aiohttp.ClientSession() as session:
        # Create a list of tasks for scraping each page
        tasks = [scrape_page(session, i * 24) for i in range(pages)]
        results = await asyncio.gather(*tasks)  # Execute all tasks in parallel

        total_inserted = 0
        for page_data in results:
            for prop in page_data:
                if not prop[
                    "link"
                ]:  # Skip the property if the link is missing (essential for uniqueness)
                    logging.warning(f"Skipping property due to missing link: {prop}")
                    continue
                try:
                    # Insert the property into the DB. 'INSERT OR IGNORE' prevents duplicates based on the 'link' field.
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO properties (price, address, description, bedrooms, link)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            prop["price"],
                            prop["address"],
                            prop["description"],
                            prop["bedrooms"],
                            prop["link"],
                        ),
                    )
                    if (
                        cursor.rowcount > 0
                    ):  # rowcount > 0 indicates a row was inserted (not ignored)
                        total_inserted += 1
                except Exception as e:
                    logging.error(
                        f"Database insertion error for link {prop['link']}: {e}"
                    )

        conn.commit()  # Save changes to the database
        logging.info(f"[✔] Saving completed: {total_inserted} new properties saved.")

    # Generate CSV filename with current date (YYYY-MM-DD format)
    csv_filename = (
        f"output/rightmove_properties_{datetime.now().strftime('%Y-%m-%d')}.csv"
    )

    # Export DB content to a CSV file
    try:
        cursor.execute(
            "SELECT price, address, description, bedrooms, link, scraped_at FROM properties"
        )
        rows = cursor.fetchall()  # Retrieve all rows
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["price", "address", "description", "bedrooms", "link", "scraped_at"]
            )  # Write header row
            writer.writerows(rows)  # Write all data rows
        logging.info(
            f"[✔] CSV export completed to '{csv_filename}' with {len(rows)} rows."
        )
    except Exception as e:
        logging.error(f"[✘] Error during CSV export: {e}")

    finally:
        conn.close()  # Close the database connection even if an error occurs
        logging.info("Database connection closed.")
        logging.info("Script finished.")
        print("Script completed. Check the log file for details.")


if __name__ == "__main__":
    start_time = datetime.now()
    logging.info(f"Script started at {start_time}")

    pages_to_scrape = 20  # Number of pages to scrape
    asyncio.run(scrape_and_save_properties(pages=pages_to_scrape))

    end_time = datetime.now()
    logging.info(f"Script ended at {end_time} (Duration: {end_time - start_time})")

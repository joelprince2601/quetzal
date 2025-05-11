import asyncio
import os
from crawl4ai import AsyncWebCrawler

# List of target websites
websites = [
    "https://www.moneycontrol.com/",
    "https://www.nseindia.com/",
    "https://www.bseindia.com/",
    "https://www.screener.in/",
    "https://in.investing.com/",
    "https://economictimes.indiatimes.com/markets",
    "https://www.tickertape.in/",
    "https://www.equitymaster.com/",
    "https://www.marketsmojo.com/",
    "https://www.cmie.com/"
]

# Output directory
output_dir = "scraped_data"
os.makedirs(output_dir, exist_ok=True)

async def scrape_website(url):
    """Scrapes data from a given website and saves it to a file."""
    async with AsyncWebCrawler() as crawler:
        try:
            result = await crawler.arun(url=url)
            filename = os.path.join(output_dir, f"{url.split('//')[1].split('.')[0]}.txt")
            with open(filename, "w", encoding="utf-8") as file:
                file.write(result.markdown)
            print(f"Data saved for {url}")
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

async def main():
    """Initiates scraping for all websites."""
    tasks = [scrape_website(url) for url in websites]
    await asyncio.gather(*tasks)

# Run the async function
asyncio.run(main())
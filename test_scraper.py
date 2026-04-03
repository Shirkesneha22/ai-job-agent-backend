import asyncio
from scraper import scrape_lever, scrape_greenhouse

async def test_scraper():
    print("Testing Lever scraper...")
    try:
        lever_jobs = await scrape_lever()
        print(f"Scraped {len(lever_jobs)} lever jobs.")
    except Exception as e:
        print(f"Lever scraper failed: {e}")

    print("Testing Greenhouse scraper...")
    try:
        greenhouse_jobs = await scrape_greenhouse()
        print(f"Scraped {len(greenhouse_jobs)} greenhouse jobs.")
    except Exception as e:
        print(f"Greenhouse scraper failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraper())

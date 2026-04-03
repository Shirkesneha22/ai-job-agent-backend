import asyncio
from playwright.async_api import async_playwright
import re

async def scrape_lever():
    """Scrapes jobs from Lever job board."""
    jobs = []
    async with async_playwright() as p:
        try:
            # Note: In a real-world scenario, you would need specific company URLs or a search page.
            # This is a generic implementation.
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Example Lever company page (change as needed)
            await page.goto("https://jobs.lever.co/lever", timeout=60000)
            
            # Wait for job postings to load
            await page.wait_for_selector(".posting", timeout=10000)
            job_elements = await page.query_selector_all(".posting")
            
            for el in job_elements:
                title_el = await el.query_selector("h5")
                title = await title_el.inner_text() if title_el else "Unknown Role"
                
                link_el = await el.query_selector("a.posting-title")
                link = await link_el.get_attribute("href") if link_el else ""
                
                company_el = await el.query_selector(".posting-categories .company")
                company = await company_el.inner_text() if company_el else "Lever Company"
                
                # Check for developer roles
                if re.search(r"developer|engineer|software|data|fullstack", title, re.IGNORECASE):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "link": link,
                        "description": f"Position: {title} at {company}."
                    })
            
            await browser.close()
            print(f"Scraped {len(jobs)} jobs from Lever.")
        except Exception as e:
            print(f"Error scraping Lever: {e}")
            if 'browser' in locals():
                await browser.close()
    return jobs

async def scrape_greenhouse():
    """Scrapes jobs from Greenhouse job board."""
    jobs = []
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Example Greenhouse company page (change as needed)
            await page.goto("https://boards.greenhouse.io/greenhouse", timeout=60000)
            
            # Wait for job posts to load
            await page.wait_for_selector(".job-post", timeout=10000)
            job_elements = await page.query_selector_all(".job-post")
            
            for el in job_elements:
                title_el = await el.query_selector("a")
                title = await title_el.inner_text() if title_el else "Unknown Role"
                
                link = await title_el.get_attribute("href") if title_el else ""
                if link and not link.startswith("http"):
                    link = "https://boards.greenhouse.io" + link
                    
                company = "Greenhouse Company"
                
                if re.search(r"developer|engineer|software|data|fullstack", title, re.IGNORECASE):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "link": link,
                        "description": f"Position: {title} at {company}."
                    })
            
            await browser.close()
            print(f"Scraped {len(jobs)} jobs from Greenhouse.")
        except Exception as e:
            print(f"Error scraping Greenhouse: {e}")
            if 'browser' in locals():
                await browser.close()
    return jobs

import requests
import re
import xml.etree.ElementTree as ET
import asyncio

ALLOWED_ROLES_REGEX = r"frontend|web developer|react|full\s*stack|software developer|software engineer"

def filter_role(title):
    return bool(re.search(ALLOWED_ROLES_REGEX, title.lower()))

def is_valid_link(link):
    if not link:
        return False
    link_lower = link.lower()
    return "job" in link_lower or "apply" in link_lower

def fetch_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.text
        return ""
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

async def scrape_weworkremotely():
    """Scrapes jobs from WeWorkRemotely via RSS feed."""
    jobs = []
    url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    content = fetch_content(url)
    
    if content:
        try:
            root = ET.fromstring(content)
            for item in root.findall(".//item"):
                title_text = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                
                # Title format is usually "Company: Job Title"
                parts = title_text.split(":", 1)
                if len(parts) == 2:
                    company = parts[0].strip()
                    title = parts[1].strip()
                else:
                    company = "Unknown"
                    title = title_text.strip()
                
                if filter_role(title) and is_valid_link(link):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "link": link
                    })
        except Exception as e:
            print(f"Error parsing WWR XML: {e}")

    print(f"Scraped {len(jobs)} from WeWorkRemotely.")
    return jobs

async def scrape_remoteok():
    """Scrapes jobs from RemoteOK via their public JSON API."""
    jobs = []
    url = "https://remoteok.com/api"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # First object in array is usually legal/disclaimer
            for item in data:
                if "legal" in item:
                    continue
                title = item.get("position", "")
                company = item.get("company", "")
                link = item.get("url", "")
                
                if filter_role(title) and is_valid_link(link):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "link": link
                    })
    except Exception as e:
        print(f"Error fetching/parsing RemoteOK: {e}")

    print(f"Scraped {len(jobs)} from RemoteOK.")
    return jobs

async def scrape_wellfound():
    """Scrapes jobs from Wellfound. Stub for returning empty results or relying on other sources."""
    # Wellfound aggressively blocks scraping. WWR and RemoteOK typically give plenty of jobs.
    print("Skipping direct Wellfound scrape (requires JS/Bot-bypass), relying on WWR and RemoteOK.")
    return []

def clean_and_limit_jobs(jobs):
    # Ensure no duplicates based on link
    unique_links = set()
    clean_jobs = []
    
    for job in jobs:
        link = job["link"]
        if link not in unique_links:
            unique_links.add(link)
            clean_jobs.append(job)
            
    # Limit to 10-20 jobs. Let's return 15.
    return clean_jobs[:15]

# Legacy compat if any other file was importing it directly
async def scrape_lever():
    return []

async def scrape_greenhouse():
    return []

async def run_all_scrapers():
    """Run all scrapers and return the combined cleaned list."""
    results = await asyncio.gather(
        scrape_remoteok(),
        scrape_weworkremotely(),
        scrape_wellfound()
    )
    
    all_jobs = []
    for res in results:
        all_jobs.extend(res)
        
    final_jobs = clean_and_limit_jobs(all_jobs)
    print(f"Total valid clean jobs found: {len(final_jobs)}")
    return final_jobs

if __name__ == "__main__":
    jobs = asyncio.run(run_all_scrapers())
    for j in jobs:
        print(j)

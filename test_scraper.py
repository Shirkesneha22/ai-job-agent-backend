import requests
from bs4 import BeautifulSoup
import re

ALLOWED_ROLES_REGEX = r"frontend|web developer|react|full\s*stack|software developer|software engineer"

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.text if response.status_code == 200 else ""
    except Exception as e:
        print(e)
        return ""

def filter_role(title):
    return bool(re.search(ALLOWED_ROLES_REGEX, title.lower()))

def fix_link(raw_link, base_url):
    if not raw_link: return ""
    if raw_link.startswith("http"): link = raw_link
    elif raw_link.startswith("//"): link = "https:" + raw_link
    elif raw_link.startswith("/"): link = base_url + raw_link
    else: link = base_url + "/" + raw_link
    
    if "job" in link.lower() or "apply" in link.lower():
        return link
    # remoteok sometimes just links to /remote-jobs/... which has job. 
    # Let's ensure it's not empty and returns.
    return link

def scrape_weworkremotely():
    html = fetch_html("https://weworkremotely.com/categories/remote-programming-jobs")
    jobs = []
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for article in soup.select("article ul li a"):
            parent = article.parent
            if parent and parent.get("class") and "view-all" in parent.get("class", []): continue
            
            title_node = article.select_one(".title")
            company_node = article.select_one(".company")
            
            if title_node and company_node:
                title = title_node.text.strip()
                company = company_node.text.strip()
                
                raw_link = article.get("href")
                link = fix_link(raw_link, "https://weworkremotely.com")
                
                if filter_role(title) and link:
                    if "job" in link.lower() or "apply" in link.lower() or "remote-jobs" in link.lower():
                        jobs.append({"title": title, "company": company, "link": link})
    print("weworkr:", jobs[:2])
    return jobs

def scrape_remoteok():
    html = fetch_html("https://remoteok.com/remote-dev-jobs")
    jobs = []
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for tr in soup.select("tr.job"):
            title_node = tr.select_one("h2")
            company_node = tr.select_one("h3")
            link_node = tr.select_one("a.preventLink")
            
            if title_node and company_node and link_node:
                title = title_node.text.strip()
                company = company_node.text.strip()
                raw_link = link_node.get("href")
                link = fix_link(raw_link, "https://remoteok.com")
                
                if filter_role(title) and link:
                     if "job" in link.lower() or "apply" in link.lower() or "remote-jobs" in link.lower():
                        jobs.append({"title": title, "company": company, "link": link})
    print("remoteok:", jobs[:2])
    return jobs

scrape_weworkremotely()
scrape_remoteok()

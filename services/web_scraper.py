import requests
from bs4 import BeautifulSoup

def important_links(soup, base_url):
    about_links = []
    for a in soup.find_all('a', href=True):
        if 'about' in a.text.lower() or 'about' in a['href'].lower() or 'services' in a.text.lower() or 'services' in a['href'].lower():
            href = a['href']
            if not href.startswith('http'):
                href = base_url.rstrip('/') + '/' + href.lstrip('/')
            about_links.append(href)
    return list(set(about_links))

def scrape_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup.text

def scrape_company_homepage(domain):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    url = f"https://{domain}"
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = []
    content.append(soup.text)

    important_link = important_links(soup, url)

    for meta_tag in important_link:
        content.append(scrape_page(meta_tag))

    return {
        "content": content,
        "important_links": important_link,
    }
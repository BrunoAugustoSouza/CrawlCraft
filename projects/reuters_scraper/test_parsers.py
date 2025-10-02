from curl_cffi import requests
from bs4 import BeautifulSoup
from ipdb import set_trace
import re
import json
from urllib.parse import urlparse
import time, os
from swiftshadow import QuickProxy

# Fetch HTTPS proxies from the US
# Use ProxyInterface for more control
proxy_list = QuickProxy(countries=['US'], protocol='http')
proxies = {'http':proxy_list}
print(proxies)
url = "https://www.reuters.com/business/google-says-hackers-are-sending-extortion-emails-executives-2025-10-02/"
 
path_parts = urlparse(url).path.strip("/").split("/")
section = path_parts[0]
url_path = path_parts[1]
response = requests.get(url, impersonate="chrome_android", proxies=proxies)

soup = BeautifulSoup(response.text, "html.parser")


def get_title(soup):
    # Busca o h1 que tenha o atributo data-testid="Heading"
    title = ""
    h1_tag = None
    h1_tag = soup.find("h1", {"data-testid": "Heading"})


    if not h1_tag:
        title_tag = soup.find("title")
        title = None
        if title_tag:
            title = title_tag.text.split('|')[0].strip()
    else:
        title = h1_tag.text    
    return title

def get_article_txt(soup):
    article_txt = ""
    # Regex para pegar data-testid que começa com "paragraph-" seguido de número
    paragraph_divs = soup.find_all("div", {"data-testid": re.compile(r"^paragraph-\d*")})

    paragraphs = [div.get_text(strip=True) for div in paragraph_divs]
    article_txt = "\n".join(paragraphs)
    return article_txt

title = get_title(soup)
article_txt = get_article_txt(soup)

data = {
    "url":url,
    "snapshot_time":str(time.time()),
    "section":section,
    "title": title,
    "article": article_txt
}

# Salvar em arquivo JSON
if not os.path.isdir(f"reuters_scraper/data/{section}"):
    os.mkdir(f"reuters_scraper/data/{section}")
with open(f"reuters_scraper/data/{section}/{url_path}.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
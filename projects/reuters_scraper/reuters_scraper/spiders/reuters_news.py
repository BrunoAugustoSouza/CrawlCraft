import scrapy
import re
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from curl_cffi import requests
from swiftshadow import QuickProxy
from reuters_scraper.items import ReutersScraperItem
from ipdb import set_trace

class ReutersNewsSpider(scrapy.Spider):
    name = "reuters_news"
    sitemap_url = "https://www.reuters.com/arc/outboundfeeds/sitemap-index/?outputType=xml"

    def start_requests(self):
        resp = requests.get(self.sitemap_url, impersonate="chrome")
        root = ET.fromstring(resp.text)
        ns = {
            "ns": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "image": "http://www.google.com/schemas/sitemap-image/1.1",
        }
        
        sitemap_links = root.findall("ns:sitemap", ns)
        sitemap = sitemap_links[0].find("ns:loc", ns).text
        yield scrapy.Request(url=sitemap, callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        root = ET.fromstring(response.text)
        ns = {
            "ns": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "image": "http://www.google.com/schemas/sitemap-image/1.1",
        }
        proxy_list = QuickProxy(countries=["US"], protocol="http")
        for url_elem in root.findall("ns:url", ns)[:100]:
            loc = url_elem.find("ns:loc", ns).text
            try:
                if proxy_list:
                    proxies = {"http": proxy_list[0]}
                r = requests.get(loc, impersonate="chrome_android", proxies=proxies)
                if r.status_code == 200:
                    yield from self.parse_article(r)

            except Exception as e:
                self.logger.error(f"Erro ao acessar {loc}: {e}")

    def parse_article(self, resp):
        item = ReutersScraperItem()
        url = resp.url
        soup = BeautifulSoup(resp.text, "html.parser")
        path_parts = urlparse(url).path.strip("/").split("/")
        section = path_parts[0]

        item["title"] = self.get_title(soup)
        item["url"] = url
        item["section"] = section
        item["snapshot_time"] = time.time()
        item["content"] = self.get_content(soup)

        yield item
        
    def get_title(self, soup):
        h1_tag = soup.find("h1", {"data-testid": "Heading"})
        if h1_tag:
            return h1_tag.get_text(strip=True)

        title_tag = soup.find("title")
        if title_tag:
            return title_tag.text.split("|")[0].strip()

        return ""

    def get_content(self, soup):
        paragraph_divs = soup.find_all(
            "div", {"data-testid": re.compile(r"^paragraph-\d*")}
        )
        return "\n".join(div.get_text(strip=True) for div in paragraph_divs if div.get_text(strip=True))
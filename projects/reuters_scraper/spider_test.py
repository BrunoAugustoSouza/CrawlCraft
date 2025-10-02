import xml.etree.ElementTree as ET
from swiftshadow import QuickProxy
from curl_cffi import requests
from ipdb import set_trace
def parse_sitemap(response):
    set_trace()
    root = ET.fromstring(response.body)
    ns = {
        "ns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "image": "http://www.google.com/schemas/sitemap-image/1.1",
    }
    print("LINKS ENCONTRADOS: ", root.findall("ns:sitemap", ns)[:100])
    for url_elem in root.findall("ns:sitemap", ns)[:100]:
        loc = url_elem.find("ns:loc", ns).text
        try:
            proxy_list = QuickProxy(countries=["US"], protocol="http")
            proxies = None
            if proxy_list:
                proxies = {"http": proxy_list[0], "https": proxy_list[0]}

            r = requests.get(loc, impersonate="chrome_android", proxies=proxies)
            if r.status_code == 200:
                pass

        except Exception as e:
            pass
            
if __name__=='__main__':
    url="https://www.reuters.com/arc/outboundfeeds/sitemap-index/?outputType=xml"
    response = requests.get(url, impersonate='chrome')
    parse_sitemap(response=response)
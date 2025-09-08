# scraper.py
from playwright.sync_api import sync_playwright
from urllib.parse import quote
import pandas as pd
import time
from ipdb import set_trace
from bs4 import BeautifulSoup
import re
from common.db import Session, HomesUrl


def get_first_page_info(country:str, city: str, checkin:str, 
                        checkout:str, adults:int, scrape_job_id:str) -> pd.DataFrame:
    # Formatação da cidade na URL
    city_url = f"{city.replace(' ', '-')}" + "--" + f"{country.replace(' ', '-')}"
    refinement_path = quote("/homes")  # codifica para %2Fhomes

    # Montagem da URL final
    search_url = (
        f"https://www.airbnb.com/s/{city_url}/homes"
        f"?refinement_paths%5B%5D={refinement_path}"
        f"&date_picker_type=calendar"
        f"&checkin={checkin}"
        f"&checkout={checkout}"
        f"&adults={adults}"
        f"&source=structured_search_input_header"
        f"&search_type=search_query"
    )

    meta_data_list = []
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            page.goto(search_url, wait_until="networkidle")
            page.wait_for_selector('div[itemprop="itemListElement"]', timeout=10000)
            # Obter o HTML da página
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            # Encontrar as divs com itemprop="itemListElement"
            
            item_list_divs = soup.find_all("div", itemprop="itemListElement")
            for div in item_list_divs:
                # Pegando apenas as <meta> filhas diretas
                meta_children = div.find_all("meta", recursive=False)
                
                # Dicionário para armazenar os pares itemprop: content
                meta_info = {}
                for meta in meta_children:
                    itemprop = meta.get("itemprop")
                    content = meta.get("content")
                    if itemprop and content:
                        meta_info[itemprop] = content
                
                # Adiciona ao resultado apenas se tiver pelo menos um par
                if meta_info:
                    meta_data_list.append(meta_info)
                

            df_imoveis = pd.DataFrame(meta_data_list)
            df_imoveis['url'] = df_imoveis['url'].map(lambda x: x.split('?')[0])
            with Session() as session:
                # Converte o DataFrame em objetos HomesUrl
                homes = [
                    HomesUrl(scrape_job_id=scrape_job_id, name=row['name'], position=row['position'], url=row['url']) 
                    for _, row in df_imoveis.iterrows()
                ]
                # Adiciona todos os objetos e faz commit
                session.add_all(homes)
                session.commit()
            browser.close()
    except Exception as e:
        print(f"Error while scraping data with Playwright: ", e)
    return df_imoveis

if __name__=='__main__':
    import uuid
    city='New York'
    country='USA'
    checkin='2025-10-10'
    checkout='2025-10-12'
    adults=2
    scraper_job_id=str(uuid.uuid4())
    a=get_first_page_info(country, city, checkin, checkout, adults, scraper_job_id)
    pass
    
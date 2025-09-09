import json
import uuid
import os,sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipdb import set_trace
import os

import pandas as pd

from common.price import get_price, get_details
from common.scraper import get_first_page_info
from common.parser import clean_price_to_float, parse_price_from_json
from common.db import Session, Price

def run_parallel_scraping(urls, check_in, check_out, adults, currency, max_workers=10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Passando todos os parâmetros para a função
        future_to_url = {
            executor.submit(scrape_airbnb, url, check_in, check_out, adults, currency): url
            for url in urls
        }

        results = []
        for future in as_completed(future_to_url):
            try:
                result = future.result()  # força exceção se ocorrer
                results.append(result)
            except Exception as e:
                url = future_to_url[future]
                print(f"Erro ao processar {url}: {e}")
        return results


def delete_all_jsons(folderpath:str):
    files = os.listdir(folderpath)
    for file in files:
        filepath = os.path.join(folderpath, file)
        os.remove(filepath)

def scrape_airbnb(url:str, check_in:str, check_out:str, adults:int, currency:str):
    room_id = url.split('/')[-1]
    proxy_url = ""  # Proxy URL (if needed)
    language="en"
    
    data, price_input, cookies = get_details(url, language, proxy_url)
    product_id = price_input["product_id"]
    api_key = price_input["api_key"]
    currency = currency.upper()
    adults=1
    data = get_price(api_key, cookies, price_input["impression_id"], product_id, 
                check_in, check_out, adults, currency, language, proxy_url)

    data['roomId'] = room_id
    data['checkIn'] = check_in
    data['checkOut'] = check_out
    data['language'] = language
    data['productId'] = product_id
    data['#adults'] = adults
    data['currency'] = currency
    data['url'] = url
    
    with open(f'data/jsons/{room_id}.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))

def run_scraper(country, city, checkin, checkout, adults, currency):
    delete_all_jsons('data/jsons/')
    scrape_job_id = str(uuid.uuid4())
    try:
        df_homes = get_first_page_info(country, city, checkin, checkout, adults, scrape_job_id)
    except Exception as e:
        df_homes=None
        print("Error: ", e)
        sys.exit()
        
    rooms_urls = df_homes['url'].to_list()
    run_parallel_scraping(rooms_urls, checkin, checkout, adults, currency, max_workers=10)
    files = os.listdir('data/jsons/')
    jsons_files = [file for file in files if file.endswith('.json')]
    json_parsed_list = []
    for json_filename in jsons_files:
        json_filepath = os.path.join('data', 'jsons', json_filename)
        json_parsed_list.append(parse_price_from_json(json_filepath))
        
    price_columns = ['priceTotal', 'discountedPrice', 
                     'originalPrice', 'priceNightTotal', 
                     'longStayDiscount', 'resortFee', 'taxesAndFees',
                     'priceAfterDiscount', 'numberOfNights']
    
    output = pd.DataFrame(json_parsed_list)
    for col in price_columns:
        output[col] = output[col].apply(clean_price_to_float)
    
    output.sort_values(['isPropertyAvailable', 'priceTotal'], ascending=[False, False], inplace=True)
    
    date_columns = ['checkIn', 'checkOut']
    output['scrapeJobId'] = scrape_job_id
    for col in date_columns:
        output[col] = pd.to_datetime(output[col], errors='coerce')
    with Session() as session:
        output_prices = [
           Price(**row.to_dict()) for _, row in output.iterrows()
        ]
        # Adiciona todos os objetos e faz commit
        session.add_all(output_prices)
        session.commit()
    # output.to_csv('data/output.csv', index=False, sep=';', encoding='utf-8')
    return output
    

if __name__=='__main__':
    pass
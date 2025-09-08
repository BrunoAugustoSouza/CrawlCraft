import json
from common.utils import get_nested_value
import pandas as pd
import os
import re

def parse_price_from_json(json_path:str) -> dict:
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
    price_data_json = json.loads(content)
    price = get_nested_value(price_data_json, 'main.price')
    available = False
    
    if price and isinstance(price, str):
        price = price.replace('\xa0', ' ')
        available=True
    discounted_price =get_nested_value(price_data_json, 'main.dicountedPrice')
    
    if discounted_price and isinstance(discounted_price, str):
        discounted_price = discounted_price.replace('xa0', ' ')
    original_price = get_nested_value(price_data_json, 'main.originalPrice')
    
    if original_price and isinstance(original_price, str):
        original_price = original_price.replace('xa0', ' ')
    
    details = get_nested_value(price_data_json, 'details')
    cleaned_details = None
    if details and isinstance(details, dict):
        details = get_nested_value(price_data_json, 'details')
        cleaned_details= {k.replace('\xa0', ' '): v.replace('\xa0', ' ') for k, v in details.items()}

    
    return {
        'isPropertyAvailable':available,
        'url':get_nested_value(price_data_json, 'url'),
        'roomId':get_nested_value(price_data_json, 'roomId'),
        'checkIn':get_nested_value(price_data_json, 'checkIn'),
        'checkOut':get_nested_value(price_data_json, 'checkOut'),
        'productId':get_nested_value(price_data_json, 'productId'),
        'adults':get_nested_value(price_data_json, '#adults'),
        'currency':get_nested_value(price_data_json, 'currency'),
        'priceTotal':price,
        'discountedPrice':discounted_price,
        'originalPrice':original_price,
        # 'qualifier':get_nested_value(price_data_json, 'main.qualifier'),
        # 'details':details if not cleaned_details else cleaned_details
    } | parse_details(details if not cleaned_details else cleaned_details)



def parse_details(details: dict):
    if details is None:
        return {
        'priceNightTotal':None,
        'longStayDiscount': None,
        'resortFee': None,
        'taxesAndFees': None,
        'priceAfterDiscount': None,
        'numberOfNights': None
    }
    long_stay_discount = details.get('Long stay discount', None)
    resort_fee = details.get('Resort fee', None)
    taxes_and_fees = details.get('Taxes and fees', None)
    price_after_discount = details.get('Price after discount', None)
    
    number_of_nights = None
    price_per_night = None
    # Iterate through the keys to find the one matching the pattern '\d+ nights'
    for key in details.keys():
        match = re.search(r'(\d+)\s*nights', key)
        if match:
            price_per_night = details.get(key, None)
            number_of_nights = int(match.group(1))
            break # Stop once the key is found

    # You can return these values, or process them further as needed
    return {
        'priceNightTotal':price_per_night,
        'longStayDiscount': long_stay_discount,
        'resortFee': resort_fee,
        'taxesAndFees': taxes_and_fees,
        'priceAfterDiscount': price_after_discount,
        'numberOfNights': number_of_nights
    }
    

def clean_price_to_float(price_str):
    if pd.isna(price_str):  
        return None
    price_str = str(price_str) 
    match = re.search(r'(\d[\d\.,]*)', price_str)

    if match:
        number_str = match.group(1)

        number_str = number_str.replace(',', '')
        try:
            return float(number_str)
        except ValueError:
            return None
    return None


if __name__=='__main__':
    pass
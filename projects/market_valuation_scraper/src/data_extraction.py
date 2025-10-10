#fear and greed index
import requests
import json

headers = {
    'accept': '*/*',
    'accept-language': 'pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'if-none-match': 'W/2666142332818888819',
    'origin': 'https://edition.cnn.com',
    'priority': 'u=1, i',
    'referer': 'https://edition.cnn.com/',
    'sec-ch-ua': '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
}


def fetch_api_response():
    response = requests.get('https://production.dataviz.cnn.io/index/fearandgreed/graphdata', headers=headers)
    return response
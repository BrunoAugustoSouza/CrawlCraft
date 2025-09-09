from common.utils import *
from bs4 import BeautifulSoup
from curl_cffi import requests
import json
from urllib.parse import urlencode

regxApiKey = re.compile(r'"key":".+?"')
regexLanguage = re.compile(r'"language":".+?"')

def from_details(meta):
    ev = meta["data"]["presentation"]["stayProductDetailPage"]["sections"]["metadata"]["loggingContext"]["eventDataLogging"]
    data = {
        "coordinates": {
                "latitude":         get_nested_value(ev,"listingLat",0),
                "longitude":        get_nested_value(ev,"listingLng",0),
        },
        "room_type":                get_nested_value(ev,"roomType",""),
        "is_super_host":            get_nested_value(ev,"isSuperhost",""),
        "home_tier":                get_nested_value(ev,"homeTier",""),
        "person_capacity":          get_nested_value(ev,"personCapacity",0),
        "rating":{
            "accuracy":             get_nested_value(ev,"accuracyRating",0),
            "checking":             get_nested_value(ev,"checkinRating",0),
            "cleanliness":          get_nested_value(ev,"cleanlinessRating",0),
            "communication":        get_nested_value(ev,"communicationRating",0),
            "location":             get_nested_value(ev,"locationRating",0),
            "value":                get_nested_value(ev,"valueRating",0),
            "guest_satisfaction":   get_nested_value(ev,"guestSatisfactionOverall",0),
            "review_count":         get_nested_value(ev,"visibleReviewCount",0),
        },
        "house_rules":{
            "aditional":"",
            "general": [],
        },
        "host":{
                "id":"",   
                "name":"",  
                "joined_on":"",  
                "description":"",  
        },
        "sub_description":{
            "title":"",
            "items": [],
        },
        "amenities": [],
        "co_hosts":[],
        "images":[],
        "location_descriptions":[],
        "highlights":[],
    }
    data["is_guest_favorite"] = False

    sections = get_nested_value(meta,"data.presentation.stayProductDetailPage.sections.sections",[])
    for section in sections:
        if "section" in section:
            section_data = get_nested_value(section,"section",{})
            if "isGuestFavorite" in section_data:
                data["is_guest_favorite"] = section_data["isGuestFavorite"]


    sd = get_nested_value(meta,"data.presentation.stayProductDetailPage.sections.sbuiData")
    for section in get_nested_value(sd,"sectionConfiguration.root.sections",[]):
        typeName=get_nested_value(section,"sectionData.__typename","")
        if typeName == "PdpHostOverviewDefaultSection":
            data["host"]={
                "id" :  get_nested_value(section,"sectionData.hostAvatar.loggingEventData.eventData.pdpContext.hostId",""),
                "name": get_nested_value(section,"sectionData.title",""),
            }
        elif typeName == "PdpOverviewV2Section":
            data["sub_description"]["title"]=get_nested_value(section,"sectionData.title","")
            for item in get_nested_value(section,"sectionData.overviewItems",[]):
                data["sub_description"]["items"].append(get_nested_value(item,"title",""))

    for section in get_nested_value(meta,"data.presentation.stayProductDetailPage.sections.sections",[]):
        typeName=get_nested_value(section,"section.__typename","")
        match typeName:
            case "HostProfileSection": 
                data["host"]["id"] = get_nested_value(section,"section.hostAvatar.userID","")
                data["host"]["name"] = get_nested_value(section,"section.title","")
                data["host"]["joined_on"] = get_nested_value(section,"section.subtitle","")
                data["host"]["description"] = get_nested_value(section,"section.hostProfileDescription.htmlText","")
                for cohost in get_nested_value(section,"section.additionalHosts",[]):
                    data["co_hosts"].append({"id":cohost.get("id",""),"name":cohost.get("name","")})
            case "PhotoTourModalSection":  
                for mediaItem in get_nested_value(section,"section.mediaItems",[]):
                    img={
                        "title": mediaItem.get("accessibilityLabel",""),
                        "url": mediaItem.get("baseUrl",""),
                    }
                    data["images"].append(img)
            case "PoliciesSection":        
                for houseRulesSection in get_nested_value(section,"section.houseRulesSections",[]):
                    house_rule={
                        "title": houseRulesSection.get("title",""),
                        "values":[],
                    }
                    for item in houseRulesSection.get("items",[]):
                            if item.get("title","")=="Additional rules":
                                data["house_rules"]["aditional"]=get_nested_value(item,"html.htmlText","")
                                continue
                            house_rule["values"].append({"title":item.get("title","") ,"icon": item.get("icon","")})

                    data["house_rules"]["general"].append(house_rule)
            case "LocationSection":
                for locationDetail in get_nested_value(section,"section.seeAllLocationDetails",[]):
                    seeAllLocationDetail={
                        "title": locationDetail.get("title",""),
                        "content": get_nested_value(locationDetail,"content.htmlText"),
                    }
                    data["location_descriptions"].append(seeAllLocationDetail)
            case "PdpTitleSection":
                    data["title"]=section.get("title","")
                    if data["title"]=="":
                        data["title"]=get_nested_value(section,"section.title",[])
            case "PdpHighlightsSection":
                for highlitingData in get_nested_value(section,"section.highlights",[]):
                    highliting={
                        "title": highlitingData.get("title",""),
                        "subtitle": highlitingData.get("subtitle",""),
                        "icon": highlitingData.get("icon",""),
                    }
                    data["highlights"].append(highliting)
            case "PdpDescriptionSection":
                data["description"]=  get_nested_value(section,"section.htmlDescription.htmlText","")
            case "AmenitiesSection":  
                for amenityGroupRaw in get_nested_value(section,"section.seeAllAmenitiesGroups",[]):
                    amenityGroup={
                        "title": amenityGroupRaw.get("title",""),
                        "values": [],
                    }
                    for amenityRaw in amenityGroupRaw.get("amenities",[]):
                        amenity = {
                            "title":     amenityRaw.get("title",""),
                            "subtitle":  amenityRaw.get("subtitle",""),
                            "icon":      amenityRaw.get("icon",""),
                            "available": amenityRaw.get("available",""),
                        }
                        amenityGroup["values"].append(amenity)
                    data["amenities"].append(amenityGroup)
    return data



def parse_body_details(body:str):
    soup = BeautifulSoup(body, 'html.parser')
    data_deferred_state = soup.select("#data-deferred-state-0")[0].getText()
    html_data = remove_space(data_deferred_state)
    language = regexLanguage.search(body).group()
    language = language.replace('"language":"', "")
    language = language.replace('"', "")
    api_key = regxApiKey.search(body).group()
    api_key = api_key.replace('"key":"', "")
    api_key = api_key.replace('"', "")
    data = json.loads(html_data)
    details_data = data["niobeClientData"][0][1]
    return details_data, language, api_key

def parse_body_details_wrapper(body:str):
    data_raw, language, api_key = parse_body_details(body)
    data_formatted = from_details(data_raw) 
    data_formatted["language"] = language
    price_dependency_input={
        "product_id": data_raw['variables']['id'],
        "impression_id": data_raw['variables']['pdpSectionsRequest']['p3ImpressionId'],
        "api_key": api_key
    }
    return data_formatted, price_dependency_input

def get_details(room_url: str, language: str, proxy_url: str):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": language,
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    proxies = {}
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}
    response = requests.get(room_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    data_formatted, price_dependency_input=parse_body_details_wrapper(response.text)
    cookies = response.cookies
    return data_formatted, price_dependency_input, cookies

def get_price(api_key: str, cookies: list, impresion_id: str, product_id: str, checkIn: str, 
        checkOut: str, adults: int, currency: str, language: str, proxy_url: str = None) -> (str):
        ep = "https://www.airbnb.com/api/v3/StaysPdpSections/80c7889b4b0027d99ffea830f6c0d4911a6e863a957cbe1044823f0fc746bf1f"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Airbnb-Api-Key": api_key,
        }
        entension={
            "persistedQuery": {
                "version":1,
                "sha256Hash": "80c7889b4b0027d99ffea830f6c0d4911a6e863a957cbe1044823f0fc746bf1f",
            },
        }
        dataRawExtension = json.dumps(entension)
        variablesData={
            "id": product_id,
            "pdpSectionsRequest": {
                "adults":                       str(adults),
                "bypassTargetings":              False,
                "categoryTag":                   None,
                "causeId":                       None,
                "children":                      None,
                "disasterId":                    None,
                "discountedGuestFeeVersion":     None,
                "displayExtensions":             None,
                "federatedSearchId":             None,
                "forceBoostPriorityMessageType": None,
                "infants":                       None,
                "interactionType":               None,
                "layouts":                       ["SIDEBAR", "SINGLE_COLUMN"],
                "pets":                          0,
                "pdpTypeOverride":               None,
                "photoId":                       None,
                "preview":                       False,
                "previousStateCheckIn":          None,
                "previousStateCheckOut":         None,
                "priceDropSource":               None,
                "privateBooking":                False,
                "promotionUuid":                 None,
                "relaxedAmenityIds":             None,
                "searchId":                      None,
                "selectedCancellationPolicyId":  None,
                "selectedRatePlanId":            None,
                "splitStays":                    None,
                "staysBookingMigrationEnabled":  False,
                "translateUgc":                  None,
                "useNewSectionWrapperApi":       False,
                "sectionIds": ["BOOK_IT_FLOATING_FOOTER","POLICIES_DEFAULT","EDUCATION_FOOTER_BANNER_MODAL",
                        "BOOK_IT_SIDEBAR","URGENCY_COMMITMENT_SIDEBAR","BOOK_IT_NAV","MESSAGE_BANNER","HIGHLIGHTS_DEFAULT",
                        "EDUCATION_FOOTER_BANNER","URGENCY_COMMITMENT","BOOK_IT_CALENDAR_SHEET","CANCELLATION_POLICY_PICKER_MODAL"],
                "checkIn":        checkIn,
                "checkOut":       checkOut,
                "p3ImpressionId": impresion_id,
            },
        }
        dataRawVariables = json.dumps(variablesData)
        query = {
            "operationName": "StaysPdpSections",
            "locale": language,
            "currency": currency,
            "variables": dataRawVariables,
            "extensions": dataRawExtension,
        }
        url = f"{ep}?{urlencode(query)}"
        session = requests.Session()
        proxies = {}
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}

        session.cookies.update(cookies)

        response = session.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()

        data = response.json()

        sections = get_nested_value(data,"data.presentation.stayProductDetailPage.sections.sections",{})
        priceGroups = get_nested_value(data,"data.presentation.stayProductDetailPage.sections.metadata.bookingPrefetchData.barPrice.explanationData.priceGroups",[])
        finalData ={
            "raw": priceGroups,
        }
        for section in sections:
            if section['sectionId'] == "BOOK_IT_SIDEBAR":
                price_data = get_nested_value(section,"section.structuredDisplayPrice",{})
                finalData["main"]={
                        "price":get_nested_value(price_data,"primaryLine.price",{}),
                        "discountedPrice":get_nested_value(price_data,"primaryLine.discountedPrice",{}),
                        "originalPrice":get_nested_value(price_data,"primaryLine.originalPrice",{}),
                        "qualifier":get_nested_value(price_data,"primaryLine.qualifier",{}),
                }
                finalData["details"]={}
                details = get_nested_value(price_data,"explanationData.priceDetails",{})
                for detail in details:
                    for item in get_nested_value(detail,"items",{}):
                         finalData["details"][item["description"]]=item["priceString"]
                return finalData
        return finalData
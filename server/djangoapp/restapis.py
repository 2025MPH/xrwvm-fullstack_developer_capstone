# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

DEALERSHIP_CF_URL = os.getenv(
    "DEALERSHIP_CF_URL",
    default="http://localhost:5050/.json"
)


def get_request(endpoint, **kwargs):
    params = ""
    if(kwargs):
        for key,value in kwargs.items():
            params=params+key+"="+value+"&"

    request_url = backend_url+endpoint+"?"+params

    print("GET from {} ".format(request_url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except:
        # If any error occurs
        print("Network exception occurred")

def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url+"analyze/"+text
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")



# request_url = sentiment_analyzer_url+"analyze/"+text
# Add code for retrieving sentiments

def post_review(data_dict):
    request_url = backend_url+"/insert_review"
    try:
        response = requests.post(request_url,json=data_dict)
        print(response.json())
        return response.json()
    except:
        print("Network exception occurred")

def get_request_cf(url, params=None):
    print(f"GET from {url} with params {params}")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error calling cloud function:", e)
        return None


def get_dealers(state=None):
    endpoint = "/get_dealers"
    if state:
        endpoint += f"/{state}"
    
    try:
        dealers = get_request(endpoint)
        return dealers
    except Exception as e:
        print(f"Error fetching dealers: {e}")
        return []

def get_dealers_from_cf(state=None):
    params = {"state": state} if state else {}
    json_result = get_request_cf(DEALERSHIP_CF_URL, params=params)
    return parse_dealer_json(json_result)

def parse_dealer_json(json_result):
    results = []
    if json_result:
        dealers = json_result.get("entries", json_result)
        for dealer in dealers:
            results.append({
                "id": dealer.get("id"),
                "city": dealer.get("city"),
                "full_name": dealer.get("full_name"),
                "short_name": dealer.get("short_name"),
                "address": dealer.get("address"),
                "state": dealer.get("state"),
                "zip": dealer.get("zip")
            })
    return results

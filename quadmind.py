import requests
import config as setting
url_base = setting.config.quadmind_url
apiKey = setting.config.quadmind_api_key

def getConsolidatedRoutes(from_date, to_date):
   
    url = f"{url_base}consolidated-routes/search?limit=100&offset=0&from={from_date}&to={to_date}"
    #url = "https://saas.quadminds.com/api/v2/orders/search?limit=100&offset=0&from=2023-09-18&to=2023-09-19"
    headers = {
        "accept": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.get(url, headers=headers)
   
    if (response.status_code == 200):
        return response.json()['data']
    else:
        return None
    
    
def getConsolidatedRoute(id):
    
    url = f"{url_base}consolidated-routes?limit=100&offset=0&_id={id}"
    headers = {
        "accept": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.get(url, headers=headers)
   
    if (response.status_code == 200):
        return response.json()['data']
    else:
        return None
    
def getRoutes(from_date, to_date):
    
   
    url = f"{url_base}routes/search?limit=100&offset=0&from={from_date}&to={to_date}"
    #url = "https://saas.quadminds.com/api/v2/orders/search?limit=100&offset=0&from=2023-09-18&to=2023-09-19"
    headers = {
        "accept": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.get(url, headers=headers)
   
    if (response.status_code == 200):
        return response.json()['data']
    else:
        return None

def getPoi( poiId):
    url = f"{url_base}pois?limit=100&offset=0&_id={poiId}"
    headers = {
        "accept": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.get(url, headers=headers)
   
    if (response.status_code == 200):
        return response.json()['data'][0]
    else:
        return None
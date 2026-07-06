import requests
import json
from dotenv import load_dotenv
import os

class ApiExtractor:

    def __init__(self,base_url, api_token, page_size):
        self.base_url = base_url
        self.api_token = api_token
        self.page_size = page_size
        self.session = requests.session() # added session to reuse the connection for multiple API calls

        self.session.headers.update({
                                     "x-api-key": f"{self.api_token}",
                                    "Accept": "application/json",
                                    "X-Reqres-Env": "prod"
                                    })
                                    
        self.session.timeout = 30 # added timeout for sessions to avoid hanging of the request in case of network issues

    def ExtractAll(self,endpoint, param):

        if param is None:
            param = {"limit": 1, "offset": 0}

        url = self.base_url + endpoint

        response = self.session.request("GET",url,params=param, timeout=30) # added timeout for request to avoid hanging of the request in case of network issues
        print(f"response from API | URL: {response.url} | Status Code: {response.status_code}")
        

        data = response.json()
        
        
        for record in data.get("data", []):            
            yield record


# Load variables from .env file
load_dotenv()

# creating object for session which may have multiple API call for the same base url
API_KEY = os.getenv("API_KEY")
extractor = ApiExtractor(
        base_url = "https://reqres.in/api/collections/products/",
        api_token = API_KEY,
        page_size = 200
)

#define limit and offset for offset - pagination
limit = 1
offset = 0

with open("output/output_data.json",'a') as f:
    for record in extractor.ExtractAll(endpoint="records", param={"limit": limit, "offset": offset}):     
        f.write(json.dumps(record) + "\n")
        offset += limit
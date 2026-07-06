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
            param = {"limit": 1, "page": 0}

        url = self.base_url + endpoint
        
        while True:

            response = self.session.request("GET",url,params=param, timeout=30) # added timeout for request to avoid hanging of the request in case of network issues
            response.raise_for_status() # added raise_for_status to raise an exception for HTTP error responses
            print(f"response from API | URL: {response.url} | Status Code: {response.status_code}")
            
            data = response.json()
                        
            record = data.get("data", [])            
            if record is None or len(record) == 0:
                print("No more records to fetch. Exiting the loop.")
                break
            else:
                print("page :", param.get("page"), "limit:", param.get("limit"))
                param["page"] += param.get("limit")  # incrementing the page number by the limit for the next API call
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

#define limit and offset for  -> offset pagination
limit = 1
offset = 1

with open("output/output_data.json",'a') as f:
    for record in extractor.ExtractAll(endpoint="records", param={"limit": limit, "page": offset}):     
        f.write(json.dumps(record) + "\n")
        
import requests
import json

class ApiExtractor:

    def __init__(self,base_url, api_token, page_size):
        self.base_url = base_url
        self.api_token = api_token
        self.page_size = page_size
        self.session = requests.session()

        self.session.headers.update({
                "Authorization" : api_token,
                "Accept": "application/json"
        }
        )
        self.session.timeout = 30

    def ExtractAll(self,endpoint, param):

        url = self.base_url + endpoint
        response = self.session.request("get",url)
        data = response.json()        
        for record in data:            
            yield record



# creating object for session which may have multiple API call for the same base url
extractor = ApiExtractor(
        base_url = "https://jsonplaceholder.typicode.com/",
        api_token = "API KEY",      # key must be from Key management tool like AWS KMS or CSM
        page_size = 200
)


with open("output/output_data.json",'w') as f:
    for record in extractor.ExtractAll(endpoint="posts", param ={}):
        f.write(json.dumps(record) + "\n")

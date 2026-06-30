import requests
import json

class ApiExtractor:

    def __init__(self,base_url, api_token, page_size):
        self.base_url = base_url,
        self.api_token = api_token,
        self.page_size = page_size
        self.session = requests.session()

        self.session.headers.update({
                "Authorization" : api_token,
                "Accept": "application/json"
        }
        )
        self.session.timeout = 30

    def ExtractAll(self,endpoint, param):

        response = self.session.request("get","https://jsonplaceholder.typicode.com/posts/1")
        data = response.json()

        return data


    pass



# creating object for session which may have multiple API call for the same base url
extractor = ApiExtractor(
        base_url = "https://jsonplaceholder.typicode.com/",
        api_token = "API KEY",
        page_size = 200
)
# key must be from Key management tool like CSM

with open("output.json",'w') as f:
    record = extractor.ExtractAll(endpoint="posts", param ={})
    f.write(json.dumps(record))

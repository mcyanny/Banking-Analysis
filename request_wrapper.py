"""
This module is a wrapper for the FDIC API. It provides a class that can be used to make requests to the FDIC API and handle errors.
"""
import requests
import json
import pandas as pd
import os

class RequestWrapper:
    def __init__(self, base_url="https://banks.data.fdic.gov/api"):
        self.base_url = base_url
        
    def make_request(self, endpoint, params=None):
        
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params)
        
        #handles errors
        if not self.handle_response_errors(response):
            return None
        
        return response.json()
    
    def handle_response_errors(self, response):
        if response.status_code != 200:
            print(f"Error: {response.status_code}\n")
            print(response.text)
            return False
        
        return True
    
    def request_data(self, endpoint, params, format="json", output_file_name="output"):
        data = []
        offset = 0
        
        # Makes multiple requests if the total number of records is greater than the limit (10,000)
        while True:
            
            params.update({"offset": offset})
            response = self.make_request(endpoint, params)
            
            if response is None:
                break
            
            data.extend(response["data"])
            
            # Check if we reached the total
            total_records = response["meta"]["total"]
            
            # if "limit" in params:
            #     if len(data) >= params["limit"]:
            #         break
                
            if len(data) >= total_records:
                break  # No more data to fetch
            
            offset += len(response["data"])
            
        # Creates data directory
        os.makedirs("./data", exist_ok=True)
            
        # mostly for debugging:
        if format == "json":
            with open(f"./data/{output_file_name}.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
        # for analysis
        elif format in ["csv", "df"]:
            # field names from the meta data
            fields = response["meta"]["parameters"]["fields"].split(",")
            fields.append("ID")
            
            data = [entry['data'] for entry in data]
            
            data_df = pd.DataFrame(data, columns=fields)

            data_df.to_csv(f"./data/{output_file_name}.csv", index=False)
            
            if format == "df":
                return data_df

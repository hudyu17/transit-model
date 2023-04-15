# if __name__ == "__main__":
# take user input for year, select brt system
# throw data into somewhere?

import requests
import json
import pandas as pd


class BRTData(object):
    def __init__(self, name, zipcodes: list[str]) -> None:
        self.name = name
        self.years = list(map(str, [x for x in range(2013, 2021)]))

        self.income = self.pop = self.age = self.house_married = self.house_nonfam = self.house_m_single = self.house_f_single = self.car = self.biz = pd.DataFrame(index=self.years, columns=zipcodes)
        self.zipcodes = zipcodes

    def fetch_api_data(self, url: str) -> dict:
        """
        Fetches data from an API endpoint and returns the response in JSON format.

        Parameters:
        url (str): The URL of the API endpoint to fetch data from.

        Returns:
        dict: A dictionary containing the JSON response from the API endpoint.
        """
        # make the API request
        response = requests.get(url)

        # check if response is empty or not in JSON format
        if not response.content:
            raise ValueError("API response is empty")
        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise ValueError("API response is not in valid JSON format") from e
        
        # return response.json()

    def getIncome(self):
        for year in self.years:
            for zipcode in self.zipcodes:
                url = 'https://data.census.gov/api/access/data/table?g=860XX00US{zipcode}&id=ACSST5Y{year}.S1901'.format(zipcode = zipcode, year = year)
                res = self.fetch_api_data(url)

                df = pd.DataFrame.from_dict(res)
                self.income.loc[year][zipcode] = df['response']['data'][1][161]

        return self.income
    
if __name__ == "__main__":
    name = input("Name of BRT System: ")
    brt_data = BRTData(name, ['77056', '77027'])
    income_data = brt_data.getIncome()
    print(income_data)

# TODO: 
# 1. make other functions
# 2. save into the correct subdirectory (based on self.name?)
# 3. create a dict with system names: [zip codes] to run ? idk
# 4. not in this file but manual finding zipcodes lol
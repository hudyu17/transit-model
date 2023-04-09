import requests
import csv
import os
import json


def fetch_api_data(input):
    url = input[0]
    filename = input[1]
    # set the API endpoint URL and parameters
    # url = "https://data.census.gov/api/access/data/table?g=860XX00US77056:860XX00US77027:860XX00US77024:860XX00US77055&id=ACSST5Y2021.S1901"
    # url = "https://data.census.gov/api/access/data/table?g=860XX00US44104&id=ACSST5Y2019.S1901"

    # params = {"param1": "value1", "param2": "value2"}

    # make the API request
    response = requests.get(url)
    json_data = response.json()

    # Construct the path to the "raw" folder in the same directory as the script
    raw_folder_path = os.path.join(os.path.dirname(__file__), 'raw')

    # Create the "raw" folder if it does not exist
    if not os.path.exists(raw_folder_path):
        os.mkdir(raw_folder_path)

    # Construct the path to the JSON file in the "raw" folder
    json_file_path = os.path.join(raw_folder_path, filename)

    # Write the JSON data to the file
    with open(json_file_path, 'w') as f:
        json.dump(json_data, f)


if __name__ == "__main__":
    cleveland_income = ('https://data.census.gov/api/access/data/table?g=860XX00US44104&id=ACSST5Y2011.S1901', 'cleveland-income-2011.json')
    # cleveland_population = ('https://data.census.gov/api/access/data/table?g=860XX00US44104&id=ACSDP5Y2017.DP05', 'cleveland-pop-2017.json')
    # cleveland_population = ('https://data.census.gov/api/access/data/table?g=860XX00US44112&id=ACSDP5Y2015.DP05', 'cleveland-pop-2015.json')
    # cleveland_population = ('https://data.census.gov/api/access/data/table?g=860XX00US44112&id=ACSST5Y2021.S0101', 'cleveland-pop-new-2021.json')
    # houston_population = ('https://data.census.gov/api/access/data/table?g=860XX00US77024&id=ACSST5Y2016.S0101', 'houston-pop-2016.json')

    fetch_api_data(cleveland_income)

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
    # cleveland_income = ('https://data.census.gov/api/access/data/table?g=860XX00US44104&id=ACSST5Y2011.S1901', 'cleveland-income-2011.json')
    # cleveland_population = ('https://data.census.gov/api/access/data/table?g=860XX00US44104&id=ACSDP5Y2017.DP05', 'cleveland-pop-2017.json')
    # cleveland_population = ('https://data.census.gov/api/access/data/table?g=860XX00US44112&id=ACSDP5Y2015.DP05', 'cleveland-pop-2015.json')
    # cleveland_population = ('https://data.census.gov/api/access/data/table?g=860XX00US44112&id=ACSST5Y2021.S0101', 'cleveland-pop-new-2021.json')
    # houston_population = ('https://data.census.gov/api/access/data/table?g=860XX00US77024&id=ACSST5Y2016.S0101', 'houston-pop-2016.json')
    # cle_car = ('https://data.census.gov/api/access/data/table?g=860XX00US44112&id=ACSST5Y2016.S0802', 'cle-car-2016.json')
    # hou_car = ('https://data.census.gov/api/access/data/table?g=860XX00US77024&id=ACSST5Y2016.S0802', 'hou-car-2016.json')
    # cle_job = ('https://data.census.gov/api/access/data/table?id=ZBP2017.CB1700ZBP&g=860XX00US44103', 'cle-job-17.json')
    # cle_house = ('https://data.census.gov/api/access/data/table?id=ACSDP5Y2015.DP02&g=860XX00US44112', 'cle-house-15.json')
    # cle_house_new = ('https://data.census.gov/api/access/data/table?id=ACSST5Y2021.S2501&g=860XX00US44112', 'cle-house-new-21.json')
    hou_house_new = ('https://data.census.gov/api/access/data/table?id=ACSST5Y2011.S2501&g=860XX00US77027', 'hou-house-new-11.json')


    fetch_api_data(hou_house_new)

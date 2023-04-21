import requests
import json
import pandas as pd
import os
import time
from io import BytesIO
from zipfile import ZipFile

class BRTData(object):
    def __init__(self, location, zipcodes: list[str] = []) -> None:
        self.name = location
        self.years = list(map(str, [x for x in range(2013, 2021)]))
        self.zipcodes = zipcodes

        self.income = pd.DataFrame(index=self.years, columns=zipcodes)
        self.pop = pd.DataFrame(index=self.years, columns=zipcodes)
        self.age = pd.DataFrame(index=self.years, columns=zipcodes)
        self.house_married = pd.DataFrame(index=self.years, columns=zipcodes)
        self.house_nonfam = pd.DataFrame(index=self.years, columns=zipcodes)
        self.house_m_single = pd.DataFrame(index=self.years, columns=zipcodes)
        self.house_f_single = pd.DataFrame(index=self.years, columns=zipcodes)
        self.car = pd.DataFrame(index=self.years, columns=zipcodes)
        self.biz = pd.DataFrame(index=self.years, columns=zipcodes)

        # Creating directory to save raw data
        # Get the absolute path to the directory containing the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate two levels up to the project directory
        project_dir = os.path.abspath(os.path.join(script_dir, "../.."))
        # Define the paths to the data directories
        data_dir = os.path.join(project_dir, "data/raw")
        loc_dir = os.path.join(data_dir, location)

        # Create the raw directory if it doesn't exist
        if not os.path.exists(loc_dir):
            os.makedirs(loc_dir)

        self.resultsLocation = loc_dir

    # --------------------------------------------
    # HELPER FUNCTIONS
    # --------------------------------------------

    def fetch_api_data(self, url: str) -> dict:
        """
        Fetches data from an API endpoint and returns the response in JSON format.

        Parameters:
        url (str): The URL of the API endpoint to fetch data from.

        Returns:
        dict: A dictionary containing the JSON response from the API endpoint.
        """
        # print(url) # for debugging

        # make the API request
        response = requests.get(url)

        # check if response is empty or not in JSON format
        if not response.content:
            return None
        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise ValueError("API response is not in valid JSON format") from e
        
    def load_existing_data(self) -> None:
        """
        Load existing data from CSV files in the results location directory and 
        assign the data to object properties in the current BRTData object.
        """
        for filename in os.listdir(self.resultsLocation):
            if filename.endswith(".csv"):
                print(filename)
                csv_path = os.path.join(self.resultsLocation, filename)
                csv_data = pd.read_csv(csv_path, index_col=0)
                csv_data = csv_data.rename_axis('year')
                setattr(self, os.path.splitext(filename)[0], csv_data)

        # Note: No checking of zipcode consistency
    
    def get_data(self, data):
        """
        Returns a property of a BRTData object.

        Parameters:
            data (str): The name of the property to return.

        Returns:
            The value of the specified property of the BRData object.
        """
        try:
            return getattr(self, data)
        except AttributeError:
            raise ValueError(f"'{BRTData.__name__}' object has no attribute '{data}'")

    # --------------------------------------------
    # DATA RETRIEVAL FUNCTIONS
    # --------------------------------------------

    def save_income(self) -> None:
        """
        Fetches median household annual income for the zip codes and years stored in the BRTData object.

        The resulting 'income' DataFrame is saved as a CSV file in the 'data/raw/{resultsLocation}' 
        directory of the BRTData object.
        """
        for year in self.years:
            for zipcode in self.zipcodes:
                url = 'https://data.census.gov/api/access/data/table?g=860XX00US{zipcode}&id=ACSST5Y{year}.S1901'.format(zipcode = zipcode, year = year)
                res = self.fetch_api_data(url)
                if not res:
                    continue

                df = pd.DataFrame.from_dict(res)
                self.income.loc[year][zipcode] = df['response']['data'][1][161]
            
            time.sleep(5)

        # Save to CSV
        path = os.path.join(self.resultsLocation, "income.csv")
        self.income.to_csv(path, index=True)
    
    def save_pop_age(self) -> None:
        """
        Fetches population and median age for the zip codes and years stored in the BRTData object.

        The resulting 'age' and 'pop' DataFrames are saved as CSV files in the 'data/raw/{resultsLocation}' 
        directory of the BRTData object.
        """
        for year in self.years:
            if year in ['2013', '2014', '2015', '2016']:
                age_index = 140
                pop_index = 270
            else: 
                age_index = 111
                pop_index = 277

            for zipcode in self.zipcodes:
                url = 'https://data.census.gov/api/access/data/table?g=860XX00US{zipcode}&id=ACSST5Y{year}.S0101'.format(zipcode = zipcode, year = year)
                res = self.fetch_api_data(url)
                if not res:
                    continue

                df = pd.DataFrame.from_dict(res)

                self.age.loc[year][zipcode] = df['response']['data'][1][age_index]
                self.pop.loc[year][zipcode] = df['response']['data'][1][pop_index]
            
            time.sleep(5)

        # Save to CSV
        age_path = os.path.join(self.resultsLocation, "age.csv")
        pop_path = os.path.join(self.resultsLocation, "pop.csv")
        
        self.age.to_csv(age_path, index=True)
        self.pop.to_csv(pop_path, index=True)
    
    def save_household(self) -> None:
        """
        Fetches household type (e.g. Married, Non-Family) for the zip codes and years stored in the 
        BRTData object.

        The resulting 'house' DataFrame is saved as a CSV file in the 'data/raw/{resultsLocation}' 
        directory of the BRTData object.
        """
        house_index = {'Married': 0, 'Nonfamily': 0, 'SingleMale': 0, 'SingleFemale': 0}

        for year in self.years:
            if year in ['2013', '2014', '2015', '2016']:
                    house_index['Married'] = 31
                    house_index['Nonfamily'] = 11
                    house_index['SingleMale'] = 174
                    house_index['SingleFemale'] = 118
            else: 
                house_index['Married'] = 863
                house_index['Nonfamily'] = 346
                house_index['SingleMale'] = 877
                house_index['SingleFemale'] = 13

            for zipcode in self.zipcodes:
                url = 'https://data.census.gov/api/access/data/table?id=ACSST5Y{year}.S2501&g=860XX00US{zipcode}'.format(zipcode = zipcode, year = year)
                res = self.fetch_api_data(url)
                if not res:
                    continue

                df = pd.DataFrame.from_dict(res)

                self.house_married.loc[year][zipcode] = df['response']['data'][1][house_index['Married']]
                self.house_nonfam.loc[year][zipcode] = df['response']['data'][1][house_index['Nonfamily']]
                self.house_m_single.loc[year][zipcode] = df['response']['data'][1][house_index['SingleMale']]
                self.house_f_single.loc[year][zipcode] = df['response']['data'][1][house_index['SingleFemale']]
            
            time.sleep(5)

        # Save to CSV
        married_path = os.path.join(self.resultsLocation, "house_married.csv")
        nonfam_path = os.path.join(self.resultsLocation, "house_nonfam.csv")
        m_single_path = os.path.join(self.resultsLocation, "house_m_single.csv")
        f_single_path = os.path.join(self.resultsLocation, "house_f_single.csv")
        
        self.house_married.to_csv(married_path, index=True)
        self.house_nonfam.to_csv(nonfam_path, index=True)
        self.house_m_single.to_csv(m_single_path, index=True)
        self.house_f_single.to_csv(f_single_path, index=True)
    
    def save_car_ownership(self) -> None:
        """
        Fetches the percentage of households that commute using public transit and have no access to a
        car for the zip codes and years stored in the BRTData object.

        The resulting 'car' DataFrame is saved as a CSV file in the 'data/raw/{resultsLocation}' 
        directory of the BRTData object.
        """
        for year in self.years:
            for zipcode in self.zipcodes:
                url = 'https://data.census.gov/api/access/data/table?g=860XX00US{zipcode}&id=ACSST5Y{year}.S0802'.format(zipcode = zipcode, year = year)
                res = self.fetch_api_data(url)
                if not res:
                    continue

                df = pd.DataFrame.from_dict(res)

                self.car.loc[year][zipcode] = df['response']['data'][1][114]
            
            time.sleep(5)

        # Save to CSV
        path = os.path.join(self.resultsLocation, "car.csv")
        self.car.to_csv(path, index=True)
    
    def save_num_businesses(self) -> None:
        """
        Fetches the number of business establishments for the zip codes and years stored in 
        the BRTData object.

        The resulting 'biz' DataFrame is saved as a CSV file in the 'data/raw/{resultsLocation}' 
        directory of the BRTData object.
        """
        for year in self.years[:6]:
            for zipcode in self.zipcodes:
                url = 'https://data.census.gov/api/access/data/table?id=ZBP{year}.CB{year_short}00ZBP&g=860XX00US{zipcode}'.format(zipcode = zipcode, year = year, year_short = year[2:])
                res = self.fetch_api_data(url)
                if not res:
                    continue

                df = pd.DataFrame.from_dict(res)

                self.biz.loc[year][zipcode] = df['response']['data'][1][15]
            
            time.sleep(5)
            
        # Save to CSV
        path = os.path.join(self.resultsLocation, "biz.csv")
        self.biz.to_csv(path, index=True)
    

class NTDData(object):
    def __init__(self) -> None:
        # A single NTDData object can handle *all* the ntd-data

        # Locating ntd-ridership directory with raw data
        script_dir = os.path.dirname(os.path.abspath(__file__))

        self.data_dir = os.path.abspath(os.path.join(script_dir, "../../data/raw/ntd-ridership"))

    # --------------------------------------------
    # HELPER FUNCTIONS
    # --------------------------------------------

    def fetch_zip_data(self, year, file_path):
        # Edge cases
        if year == 2017:
            url = requests.get('https://www.apta.com/wp-content/uploads/Resources/resources/statistics/Documents/NTD_Data/2017-National-Transit-Database.zip')
        elif year == 2015:
            url = requests.get('https://www.apta.com/wp-content/uploads/2015-NTD-Tables-APTA.zip')
        else:
            url = requests.get(f'https://www.apta.com/wp-content/uploads/{year}-National-Transit-Database.zip')

        zipfile = ZipFile(BytesIO(url.content))

        with zipfile.open(file_path) as f:
            if year == 2013:
                df = pd.read_excel(f, sheet_name="Op_Stats_Service", skiprows=[0])
            else:
                df = pd.read_excel(f, sheet_name="Metrics")

        # Filter the DataFrame to rows where column J == 'RB'
        df_filtered = df[df["Mode"] == "RB"]

        # Save the filtered data to a new CSV file
        output_file = os.path.join(self.data_dir, f'transit_data_{year}_filtered.csv')
        # output_file = os.path.join("../../data/raw/ntd-ridership", f'transit_data_{year}_filtered.csv')
        df_filtered.to_csv(output_file, index=False)

    def load_existing_data(self) -> None:
        """
        Load existing data from CSV files in the results location directory and 
        assign the data to object properties in the current NTDData object.
        """
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".csv"):
                print(filename)
                csv_path = os.path.join(self.data_dir, filename)
                csv_data = pd.read_csv(csv_path, index_col=0)
                setattr(self, os.path.splitext(filename)[0], csv_data)

    def get_data(self, data):
        """
        Returns a property of an NTDData object.

        Parameters:
            data (str): The name of the property to return.

        Returns:
            The value of the specified property of the BRData object.
        """
        try:
            return getattr(self, data)
        except AttributeError:
            raise ValueError(f"'{NTDData.__name__}' object has no attribute '{data}'")

    # --------------------------------------------
    # DATA RETRIEVAL FUNCTIONS
    # --------------------------------------------

    def save_data(self):
        # do the download like in data_retrieval_ntd.ipynb
        years = [2013] + list(range(2015, 2021))
        
        file_paths = {
            2013: '2013-Table-19-Transit-Operating-Stats.xls',
            2014: '2014-Table-19-Transit-Operating-Stats.xls',
            2015: 'Metrics.xlsm',
            2016: '2016-NTD-Metrics_0.xlsx',
            2017: 'Metrics_1.xlsm',
            2018: 'Metrics_2.xlsx',
            2019: '2019_Annual_Database_Files/Metrics_Static.xlsx',
            2020: '2020_Annual_Database_Files/Metrics_Static.xlsx'
        }

        for year in years:
            print(year)
            self.fetch_zip_data(year, file_paths[year])


if __name__ == "__main__":
    ntd = NTDData()
    ntd.save_data()
    ntd.load_existing_data()
    print(ntd.get_data('transit_data_2016_filtered'))
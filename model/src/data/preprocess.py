"""
This file processes the raw CSVs downloaded in make_dataset.py for a specific transportation system.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from transit_data import BRTData, NTDData
import os

# --------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------

def make_average(df, name) -> pd.Series:
    series_average = df.mean(axis=1)
    series_average.rename(name, inplace=True)

    return series_average

def export_csv(df, name) -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, "../.."))
    data_dir = os.path.join(project_dir, "data/processed")
    
    df.to_csv(os.path.join(data_dir, f'{name}.csv'), index=True)

# --------------------------------------------
# DATA PROCESSING FUNCTIONS
# --------------------------------------------

def process_brt_data(brt_data: BRTData) -> pd.DataFrame:
    """
    Clean and process BRTData for various metrics and return a pandas DataFrame of the resulting average values.

    Parameters:
        brt_data (BRTData): BRTData object to process.

    Returns:
        pandas.Dataframe: A pandas DataFrame of the resulting average values for each metric.
    """
    metrics = ['income', 'pop', 'age', 'house_married', 'house_nonfam', 'house_m_single', 'house_f_single', 'car', 'biz']
    series_list = []

    for metric in metrics:
        df = brt_data.get_data(metric)
        
        # Cleaning
        df.dropna(axis=1, how='all', inplace=True) # drop cols with all NaN's
        df = df.loc[:, ~(df < 0).any(axis=0)] # drop cols that feature any negative
        df = df.loc[:, df.eq(0).mean() <= 0.25] # only keep cols with 25% or fewer values that are still 0

        series_average = make_average(df, metric)
        series_list.append(series_average)

    return pd.concat(series_list, axis=1)


def process_ntd_data(ntd_data: NTDData, system: str) -> pd.DataFrame:
    """
    Clean and process NTDData and return a pandas DataFrame of the resulting values for a specific system.

    Parameters:
        ntd_data (NTDData): An object containing NTD data.
        system (str): A string representing the transit system for which data is being processed.
    
    Return type:
        pandas.DataFrame: A cleaned DataFrame containing summarized and filtered data for the specified system.
    """

    ids = {
        # 'brooklyn': '2008',
        'los_angeles': '9154',
        'boston': '1003',
        'houston': '6008',
        'orlando': '4035',
        'cleveland': '5015',
        'richmond': '3006',
        'kansas': '7005',
        'grand_rapids': '5033',
        'hartford': '1048',
        'eugene': '7',
        'indianapolis': '5050',
        'albuquerque': '6019',
        'aspen_westcliffe_glenwood_springs': '8R01-013',
        'fort_collins': '8011'
    }
    
    years = list(range(2013, 2021))
    cols = ['Unlinked Passenger Trips', 'Primary UZA\n Population', 'UZA Population', 'Mode VOMS', 'VOMS', 'Annual Vehicle Revenue Miles', 'Vehicle Revenue Miles']
    res_df = pd.DataFrame(columns = cols, index = years)

    for year in years:
        df_raw = ntd_data.get_data(f'transit_data_{year}_filtered')
        
        if year == 2013:
            df_raw = df_raw.fillna(0)
            df_raw['ID'] = df_raw['ID'].astype(int).astype(str)
            filtered_df = df_raw[df_raw["ID"].astype(str) == ids[system]]
        elif year == 2014:
            filtered_df = df_raw[df_raw["Legacy NTDID"].astype(str) == ids[system]]
        else: 
            filtered_df = df_raw[df_raw["Legacy NTD ID"].astype(str) == ids[system]]
        
        df_year = filtered_df.loc[:, filtered_df.columns.isin(cols)] 

        # Populate res_df
        for col in cols:
            try:
                res_df.at[year, col] = df_year[col][0]
            except:
                res_df.at[year, col] = np.NaN

    res_df.rename(columns={'Primary UZA\n Population': 'Primary UZA Population'}, inplace=True)

    # Merge duplicate cols
    res_df['UZA Population'].update(res_df.pop('Primary UZA Population'))
    res_df['VOMS'].update(res_df.pop('Mode VOMS'))
    res_df['Vehicle Revenue Miles'].update(res_df.pop('Annual Vehicle Revenue Miles'))

    # Column name cleaning - lowercase and space replacement
    res_df.columns= res_df.columns.str.lower()
    res_df.columns = res_df.columns.str.replace(' ', '_')

    # Cleaning values - removing commas from float fields that are mis-cast
    res_df.replace(',','', regex=True, inplace=True)
    res_df = res_df.astype({'unlinked_passenger_trips':'float'})
    res_df = res_df.astype({'uza_population':'float'})
    res_df = res_df.astype({'vehicle_revenue_miles':'float'})

    # Adjusting values off by 3 orders of magnitude somehow
    mean = res_df.mean()
    std = res_df.std()

    # Handling edge cases
    if system in ('cleveland', 'orlando'):
        res_df.loc[(abs(mean.unlinked_passenger_trips - res_df['unlinked_passenger_trips']) > std.unlinked_passenger_trips) & (res_df.index < 2015), 'unlinked_passenger_trips'] *= 1000
        res_df.loc[(abs(mean.vehicle_revenue_miles - res_df['vehicle_revenue_miles']) > std.vehicle_revenue_miles) & (res_df.index < 2015), 'vehicle_revenue_miles'] *= 1000

    elif system not in ('aspen_westcliffe_glenwood_springs', 'hartford', 'richmond'):
        res_df.loc[abs(mean.unlinked_passenger_trips - res_df['unlinked_passenger_trips']) > std.unlinked_passenger_trips, 'unlinked_passenger_trips'] *= 1000
        res_df.loc[abs(mean.vehicle_revenue_miles - res_df['vehicle_revenue_miles']) > std.vehicle_revenue_miles, 'vehicle_revenue_miles'] *= 1000

    return res_df

def process_data(brt_data: BRTData, ntd_data: NTDData, system: str) -> None:
    """
    Process BRTData and NTDData and merge the results into a dataframe. Export the merged dataframe to a CSV file.

    Args:
        brt_data (BRTData): the BRTData object containing the data to process.
        ntd_data (NTDData): the NTDData object containing the data to process.
        system (str): the name of the transit system to process. Used to filter NTD data.

    Returns:
        None. The function writes the merged dataframe to a CSV file.
    """
    brt_df = process_brt_data(brt_data)
    ntd_df = process_ntd_data(ntd_data, system)

    # Merge the dfs
    merged_df = pd.concat([brt_df, ntd_df], axis=1)
    merged_df = merged_df.round(2)
    print(merged_df)

    # Export the df to a CSV
    export_csv(merged_df, system)

def main():
    locations = ['cleveland', 'houston', 'kansas', 'richmond', 'indianapolis', 'eugene', 'albuquerque', 'aspen_westcliffe_glenwood_springs', 'fort_collins', 'hartford', 'grand_rapids', 'orlando', 'boston', 'los_angeles']
    ntd = NTDData()
    ntd.load_existing_data()
    
    for system in locations:
        brt = BRTData(system)
        brt.load_existing_data()
        process_data(brt, ntd, system)

if __name__ == "__main__":
    main()

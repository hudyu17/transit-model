"""Module to retrieve data from various sources and create the raw data file(s).

This module includes functions to extract data from APIs or other sources and 
save them into multiple raw data files. The files will be saved in the `data/raw/` 
directory under subdirectories for each BRT system.

This module utilises the BRTData class and its functions (defined in brt.py).

Example usage:
    # TODO
"""

import os
from brt import BRTData

def save_data(brt_data):
    brt_data.save_income()
    brt_data.save_pop_age()
    brt_data.save_household()
    brt_data.save_car_ownership()
    brt_data.save_num_businesses()
    # add any additional data retrieval functions here

def main():
    # TODO: EDIT from boilerplate
    # create BRTData objects and retrieve data
    data = {
        # 'cleveland': ['44112', '44104', '44103', '44106', '44114'],
        'houston': ['77056', '77027', '77024', '77055'], 
    }

    for system in data:
        brt = BRTData(system, data[system])
        save_data(brt)

if __name__ == "__main__":
    main()
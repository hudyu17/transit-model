# create the actual dataset to make predictions off of

from transit_data import BRTData
import pandas as pd
import os

def export_csv(df, name) -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(script_dir, "../../data"))
    
    df.to_csv(os.path.join(data_dir, f'{name}.csv'), index=True)

def main():
    locations = ['cleveland', 'houston', 'kansas', 'richmond', 'indianapolis', 'eugene', 'albuquerque', 'aspen_westcliffe_glenwood_springs', 'fort_collins', 'hartford', 'grand_rapids', 'orlando', 'boston', 'los_angeles']
    dfs = []

    for system in locations:
        brt = BRTData(system)
        brt.load_processed_data()

        df = brt.get_data('processed')
        df = df[df['unlinked_passenger_trips'].notna()]

        dfs.append(df)

    print(dfs)
    df_large = pd.concat(dfs)
    export_csv(df_large, 'dataset')

if __name__ == "__main__":
    main()
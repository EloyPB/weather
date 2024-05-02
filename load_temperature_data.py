import os
import numpy as np
import pandas as pd


def load_temperature_data(data_path):
    
    # get column names from header file
    with open(f'{data_path}/headers.txt', 'r') as file:
        lines = file.readlines()
    column_names = lines[1].strip().split()
    
    # load the data
    all_files = os.listdir(data_path)
    data_files = [file for file in all_files if file.startswith('CRN')]
    
    dfs = []
    for data_file in data_files:
        dfs.append(pd.read_csv(f'{data_path}/{data_file}', sep='\s+', names=column_names))
    data = pd.concat(dfs, ignore_index=True)
    
    data.replace(-9999, np.nan, inplace=True)
    
    # transform LST_YRMO into year and month columns
    data['LST_YRMO'] = pd.to_datetime(data['LST_YRMO'], format='%Y%m')
    data['YEAR'] = data['LST_YRMO'].dt.year
    data['MONTH'] = data['LST_YRMO'].dt.month
    
    return data
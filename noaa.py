import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


"""
Data downloaded from:
https://www.ncei.noaa.gov/access/crn/qcdatasets.html

Data format:
WBANNO: The station WBAN number. 
LST_YRMO: The Local Standard Time (LST) year/month of the observation. 
CRX_VN_MONTHLY: The version number of the station datalogger program that was in effect at the end of the month. Note: This field should be treated as text (i.e. string). 
PRECISE_LONGITUDE: Station longitude, using WGS-84, with a precision of 4 decimal places. 
PRECISE_LATITUDE: Station latitude, using WGS-84, with a precision of 4 decimal places. 
T_MONTHLY_MAX: The maximum air temperature, in degrees C. 
T_MONTHLY_MIN: The minimum air temperature, in degrees C. See Note F. 
T_MONTHLY_MEAN: The mean air temperature, in degrees C, calculated using the typical historical approach of (T_MONTHLY_MAX + T_MONTHLY_MIN) / 2. See Note F. 
T_MONTHLY_AVG: The average air temperature, in degrees C. See Note F. 
P_MONTHLY_CALC: The total amount of precipitation, in mm. See Note G. 
SOLRAD_MONTHLY_AVG: The average daily total solar energy received, in MJ/meter^2. See Note H. 
SUR_TEMP_MONTHLY_TYPE: Type of infrared surface temperature measurement: 'R' denotes raw (uncorrected), 'C' denotes corrected, and 'U' is unknown/missing. See Note I. 
SUR_TEMP_MONTHLY_MAX: The maximum infrared surface temperature, in degrees C. See Note J. 
SUR_TEMP_MONTHLY_MIN: The minimum infrared surface temperature, in degrees C. See Note J. 
SUR_TEMP_MONTHLY_AVG: The average infrared surface temperature, in degrees C. See Note J. 
"""

data_path = '/c/DATA/NOAA/monthly01'

# get column names from header file
with open(f'{data_path}/headers.txt', 'r') as file:
    lines = file.readlines()
column_names = lines[1].strip().split()

# load the data
all_files = os.listdir(data_path)
data_files = [file for file in all_files if file.startswith('CRN')]

dfs = []
for data_file in data_files:
    dfs.append(pd.read_csv(f'{data_path}/{data_file}', delim_whitespace=True, names=column_names))
data = pd.concat(dfs, ignore_index=True)


# find distribution of start dates
start_dates = []
wbans = data['WBANNO'].unique()
for wban in wbans:
    first_index = data.loc[data['WBANNO'] == wban].index[0]
    start_dates.append(data.loc[first_index, 'LST_YRMO'])

start_years = [int(str(start_date)[:4]) for start_date in start_dates]
plt.hist(start_years, bins=np.arange(min(start_years)-0.5, max(start_years)+0.5, 1))
plt.show()

print()
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

# drop rows with missing temperature readings
data = data[data['T_MONTHLY_MEAN'] != -9999]

# transform LST_YRMO into year and month columns
data['LST_YRMO'] = pd.to_datetime(data['LST_YRMO'], format='%Y%m')
data['YEAR'] = data['LST_YRMO'].dt.year
data['MONTH'] = data['LST_YRMO'].dt.month

# find distribution of start dates
wbans = data['WBANNO'].unique()
start_years = np.zeros(wbans.size)
for station_num, wban in enumerate(wbans):
    first_index = data.loc[data['WBANNO'] == wban].index[0]
    start_years[station_num] = data.loc[first_index, 'YEAR']

plt.hist(start_years, bins=np.arange(min(start_years)-0.5, max(start_years)+0.5, 1))

# subtract baseline temperatures
baseline_year = 2005
ok_wbans = wbans[start_years <= baseline_year - 1].tolist()
baseline = data.loc[(data['YEAR'] == baseline_year) & (data['WBANNO'].isin(ok_wbans)), ['WBANNO', 'LST_YRMO', 'MONTH', 'T_MONTHLY_MEAN']]
baseline.columns = ['WBANNO', 'LST_YRMO', 'MONTH', 'T_MONTHLY_MEAN_BASELINE']

merged_data = data[data['YEAR'] > baseline_year].merge(baseline, on=['WBANNO', 'MONTH'], how='right')
merged_data['ANOMALY'] = merged_data['T_MONTHLY_MEAN'] - merged_data['T_MONTHLY_MEAN_BASELINE']

average_anomaly = merged_data.groupby(['YEAR', 'MONTH'])['ANOMALY'].mean().reset_index()
average_anomaly['DATE'] = pd.to_datetime(average_anomaly[['YEAR', 'MONTH']].assign(DAY=1))

plt.figure()
plt.plot(average_anomaly['DATE'],  average_anomaly['ANOMALY'])

coefficients = np.polyfit(np.arange(0.0, average_anomaly.shape[0]), average_anomaly['ANOMALY'].values, 1)
poly = np.poly1d(coefficients)
plt.plot(average_anomaly['DATE'], poly(np.arange(0.0, average_anomaly.shape[0])))

plt.show()

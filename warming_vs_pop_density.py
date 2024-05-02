import os
import numpy as np
from scipy.stats import linregress
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from load_density_data import load_density_data
from load_temperature_data import load_temperature_data


# LOAD DENSITY DATA
# https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-density-rev11/data-download
density_file_path = '/c/DATA/NOAA/gpw-v4-population-density-rev11_2020_2pt5_min_asc/gpw_v4_population_density_rev11_2020_2pt5_min.asc'
density, xllcorner, yllcorner, cell_size = load_density_data(density_file_path)


# LOAD TEMPERATURE DATA
temperature_data_path = '/c/DATA/NOAA/monthly01'
temperatures = load_temperature_data(temperature_data_path)



wbans = temperatures['WBANNO'].unique()

# collect locations
longitudes = []
latitudes = []
for wban in wbans:
    first_index = temperatures[temperatures['WBANNO'] == wban].index[0]
    longitudes.append(temperatures.loc[first_index, 'PRECISE_LONGITUDE'])
    latitudes.append(temperatures.loc[first_index, 'PRECISE_LATITUDE'])

# calculate linear regressions
min_years = 3
slopes = np.full(len(wbans), np.nan)
num_years = np.empty(len(wbans))
for station_num, wban in enumerate(wbans):
    station_temperatures = temperatures.loc[temperatures['WBANNO'] == wban, ['MONTH', 'T_MONTHLY_AVG']].reset_index()
    first_month = station_temperatures.loc[0, 'MONTH']
    last_index = station_temperatures.index[station_temperatures['MONTH'] == first_month].max() - 1
    num_years[station_num] = (last_index + 1) / 12
    if last_index >= min_years*12:
        x = np.arange(last_index + 1)
        y = station_temperatures.loc[0:last_index, 'T_MONTHLY_AVG'].values
        linear_fit = linregress(x[~np.isnan(y)], y[~np.isnan(y)])
        slopes[station_num] = linear_fit.slope
        if abs(linear_fit.slope) > 0.5:
            print()


plt.figure()
plt.imshow(density, vmax=np.nanpercentile(density, 99.5), extent=[-180, 180, -90, 90])
plt.scatter(longitudes, latitudes, c=slopes)
plt.show()

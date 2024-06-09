import os
import numpy as np
from scipy.stats import linregress
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from geopy.distance import geodesic
from load_density_data import load_density_data
from load_temperature_data import load_temperature_data


# LOAD DENSITY DATA
# https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-density-rev11/data-download
density_file_path_2020 = '/c/DATA/NOAA/gpw-v4-population-density-rev11_2020_2pt5_min_asc/gpw_v4_population_density_rev11_2020_2pt5_min.asc'
density_2020, xllcorner_2020, yllcorner_2020, cell_size_2020 = load_density_data(density_file_path_2020)

density_file_path_2000 = '/c/DATA/NOAA/gpw-v4-population-density-rev11_2000_2pt5_min_asc/gpw_v4_population_density_rev11_2000_2pt5_min.asc'
density_2000, xllcorner_2000, yllcorner_2000, cell_size_2000 = load_density_data(density_file_path_2000)


# LOAD TEMPERATURE DATA
temperature_data_path = '/c/DATA/NOAA/monthly01'
temperatures = load_temperature_data(temperature_data_path)



wbans = temperatures['WBANNO'].unique()

# collect locations
longitudes = np.empty(len(wbans))
latitudes = np.empty(len(wbans))
for station_num, wban in enumerate(wbans):
    first_index = temperatures[temperatures['WBANNO'] == wban].index[0]
    longitudes[station_num] = temperatures.loc[first_index, 'PRECISE_LONGITUDE']
    latitudes[station_num] = temperatures.loc[first_index, 'PRECISE_LATITUDE']


# calculate linear regressions

# fig, ax0 = plt.subplots()

min_years = 12
slopes = np.full((len(wbans), 12), np.nan)
num_years = np.empty((len(wbans), 12))
for station_num, wban in enumerate(wbans):
    station_temperatures = temperatures.loc[temperatures['WBANNO'] == wban, ['YEAR', 'MONTH', 'T_MONTHLY_AVG']]
    station_temperatures = station_temperatures.dropna()
    
    for month in range(1, 13):
    
        month_temperatures = station_temperatures.loc[station_temperatures['MONTH'] == month]
        num_years[station_num, month-1] = month_temperatures.shape[0]
        if num_years[station_num, month-1] >= min_years:
            x = month_temperatures['YEAR'].values
            y = month_temperatures['T_MONTHLY_AVG'].values
            linear_fit = linregress(x, y)
            slopes[station_num, month-1] = linear_fit.slope
            
            # if station_num == 20:
            #     ax0.plot(x, y)
        
mean_slopes = slopes.mean(1)

density_diff = density_2020 - density_2000


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
max_value = np.nanpercentile(density_diff, 99.5)
ax.imshow(density_diff, vmin=-max_value, vmax=max_value, extent=[-180, 180, -90, 90], cmap='PRGn')
max_value = np.percentile(abs(mean_slopes), 95)
points = ax.scatter(longitudes, latitudes, c=mean_slopes, cmap='coolwarm', vmin=-max_value, vmax=max_value)
ax.coastlines()
fig.colorbar(points, fraction=0.02, label='deg / year')
plt.show()

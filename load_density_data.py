import numpy as np


def load_density_data(file_path):
    with open(file_path, 'r') as file:
        metadata = [next(file).split() for _ in range(6)]
        
    num_cols = int(metadata[0][1])
    num_rows = int(metadata[1][1])
    xllcorner = int(metadata[2][1])
    yllcorner = int(metadata[3][1])
    cell_size = float(metadata[4][1])
    no_data_value = int(metadata[5][1])
        
    data = np.loadtxt(file_path, skiprows=6)

    if data.shape[0] != num_rows or data.shape[1] != num_cols:
        raise(RuntimeError("The density data could not be read correctly"))

    data[data == no_data_value] = np.nan
    
    return data, xllcorner, yllcorner, cell_size





    
    
    
    
    
    
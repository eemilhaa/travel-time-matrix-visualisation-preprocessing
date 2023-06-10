import os
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np

import config



GRID = gpd.read_file("./data/grid/")[["YKR_ID", "geometry"]]
GRID = GRID.to_crs(epsg=4326)

def main():
    for name in get_txt_files_in_directory(Path("./data/flat_matrix/")):
        print(name)
        # read
        for mode in config.TRAVEL_MODES:
            # process modes to gjson
            pass


def get_txt_files_in_directory(directory: Path):
    """A function to get all .txt files from a firectory"""
    return [name for name in os.listdir(directory) if name.endswith(".txt")]



# for mode in config.TRAVEL_MODES:

# traveltimes = pd.read_csv(
#     f"./data/flat_matrix/travel_times_to_ {id}.txt", sep=';', na_values=['-1']
# )
# intrest_times = traveltimes[["from_id", interest_col]]

# tt_grid = GRID.merge(intrest_times, on=traveltimes["from_id"])
# tt_grid = tt_grid[["geometry", interest_col]]


# tt_grid['t'] = np.NaN

# for time in reversed(times):
#     mask = (tt_grid[interest_col] <= time)
#     tt_grid.loc[mask, "t"] = time
#     clean = tt_grid.dropna()

# catchments = clean.dissolve("t").reset_index()
# catchments = catchments[["geometry", "t"]]

if __name__ == "__main__":
    main()

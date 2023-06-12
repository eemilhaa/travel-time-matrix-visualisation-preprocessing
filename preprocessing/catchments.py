from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np

import config



GRID = gpd.read_file("./data/grid/")[["YKR_ID", "geometry"]]
GRID = GRID.to_crs(epsg=4326)

def main():
    for path in Path("./data/flat_matrix/").glob("*.txt"):
        try:
            traveltimes = pd.read_csv(
                path, sep=';', na_values=['-1']
            )
        except UnicodeDecodeError:
            continue
        ykr_id = str(path)[-11:-4]
        print(f"YKR_ID: {ykr_id}")
        # read
        for mode in config.TRAVEL_MODES:
            intrest_times = traveltimes[["from_id", mode]]

            tt_grid = GRID.merge(intrest_times, on=traveltimes["from_id"])
            tt_grid = tt_grid[["geometry", mode]]

            tt_grid['t'] = np.NaN
            for time in reversed(config.TIMES):
                mask = (tt_grid[mode] <= time)
                tt_grid.loc[mask, "t"] = time

            clean = tt_grid.dropna()
            catchments = clean.dissolve("t").reset_index()
            catchments = catchments[["geometry", "t"]]
            catchments.to_file(f"./data/catchments/{2018}_{mode}_{ykr_id}.geojson", driver="GeoJSON")
            print(f"processed {mode}")


if __name__ == "__main__":
    main()

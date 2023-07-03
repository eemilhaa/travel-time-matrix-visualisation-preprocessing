import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np

import config


GRID = gpd.read_file(Path("./data/grid/"))[["YKR_ID", "geometry"]]
GRID = GRID.to_crs(epsg=4326)


def main():
    read_path, write_path = get_args()
    for path in read_path.rglob("*.txt"):
        try:
            traveltimes = pd.read_csv(
                path, sep=";", na_values=["-1"]
            )
        except UnicodeDecodeError:
            continue
        ykr_id = str(path)[-11:-4]
        print(f"YKR_ID: {ykr_id}")
        for mode in config.TRAVEL_MODES:
            tt_grid = get_grid_with_traveltimes(GRID, traveltimes, mode)
            catchments = dissolve_grid_to_catchments(
                tt_grid, breakpoints=config.TIMES, mode=mode
            )
            catchments.to_file(
                Path(write_path / f"{2018}_{mode}_{ykr_id}.geojson"),
                driver="GeoJSON"
            )
            print(f"processed {mode}")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--read_path", type=str)
    parser.add_argument("-w", "--write_path", type=str)
    args = parser.parse_args()
    read_path = args.read_path
    write_path = args.write_path
    return Path(read_path), Path(write_path)


def get_grid_with_traveltimes(grid, traveltimes, mode):
    intrest_times = traveltimes[["from_id", mode]]
    tt_grid = grid.merge(intrest_times, on=intrest_times["from_id"])
    tt_grid = tt_grid[["geometry", mode]]
    tt_grid["t"] = np.NaN
    return tt_grid


def dissolve_grid_to_catchments(tt_grid, breakpoints, mode):
    for time in reversed(breakpoints):
        mask = (tt_grid[mode] <= time)
        tt_grid.loc[mask, "t"] = time
    clean = tt_grid.dropna()
    catchments = clean.dissolve("t").reset_index()
    catchments = catchments[["geometry", "t"]]
    return catchments


if __name__ == "__main__":
    main()

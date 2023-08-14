import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np

import config
from grid import preprocess_grid


def main():
    args = get_args()
    grid = gpd.read_file(args.grid_dir)[["YKR_ID", "geometry"]]
    grid = preprocess_grid(grid)
    for matrix_path in args.matrix_dir.rglob("*.txt"):
        try:
            matrix = pd.read_csv(
                matrix_path, sep=";", na_values=["-1"]
            )
        except UnicodeDecodeError:
            continue
        ykr_id = str(matrix_path)[-11:-4]
        print(f"YKR_ID: {ykr_id}")
        for mode in config.TRAVEL_MODES:
            tt_grid = get_grid_with_traveltimes(grid, matrix, mode)
            catchments = dissolve_grid_to_catchments(
                tt_grid, breakpoints=config.TIMES, mode=mode
            )
            catchments.to_file(
                Path(args.write_dir / f"{2018}_{mode}_{ykr_id}.geojson"),
                driver="GeoJSON"
            )
            print(f"processed {mode}")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--grid_dir", type=Path)
    parser.add_argument("-m", "--matrix_dir", type=Path)
    parser.add_argument("-w", "--write_dir", type=Path)
    paths = parser.parse_args()
    return paths


def get_grid_with_traveltimes(grid, traveltimes, mode):
    intrest_times = traveltimes[["from_id", mode]]
    tt_grid = grid.merge(intrest_times, on=intrest_times["from_id"])
    tt_grid = tt_grid[["geometry", mode]]
    tt_grid["t"] = np.NaN
    return tt_grid


def dissolve_grid_to_catchments(tt_grid, breakpoints, mode):
    for time in sorted(breakpoints, reverse=True):
        mask = (tt_grid[mode] <= time)
        tt_grid.loc[mask, "t"] = time
    clean = tt_grid.dropna()
    catchments = clean.dissolve("t").reset_index()
    catchments["t"] = catchments["t"].astype(int)  # To save a tiny bit on output size
    catchments = catchments[["geometry", "t"]]
    return catchments


if __name__ == "__main__":
    main()

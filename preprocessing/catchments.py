import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np

from config import BREAKPOINTS, TRAVEL_MODES
from grid import preprocess_grid
from minify_geojson import minify_files_in_dir


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
        for mode in TRAVEL_MODES:
            tt_grid = get_grid_with_traveltimes(grid, matrix, mode)
            catchments = dissolve_grid_to_catchments(
                tt_grid, breakpoints=BREAKPOINTS, mode=mode
            )
            write_catchments_to_geojson(
                catchments, args.year, mode, ykr_id, args.write_dir
            )
            print(f"    processed {mode}")
    minify_files_in_dir(args.write_dir)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--grid_dir", type=Path)
    parser.add_argument("-m", "--matrix_dir", type=Path)
    parser.add_argument("-w", "--write_dir", type=Path)
    parser.add_argument("-y", "--year", type=int)
    args = parser.parse_args()
    return args


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


def write_catchments_to_geojson(gdf, year, mode, ykr_id, write_dir):
    filename = f"{year}_{mode}_{ykr_id}.geojson"
    gdf.to_file(
        Path(write_dir / filename),
        driver="GeoJSON"
    )


if __name__ == "__main__":
    main()

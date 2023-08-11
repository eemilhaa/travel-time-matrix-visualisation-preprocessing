import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely import wkt

import config


GRID = gpd.read_file(Path("./data/grid/"))[["YKR_ID", "geometry"]]


def main():
    grid = preprocess_grid(GRID)
    read_path, write_path = get_paths_from_args()
    for traveltime_filepath in read_path.rglob("*.txt"):
        try:
            traveltimes = pd.read_csv(
                traveltime_filepath, sep=";", na_values=["-1"]
            )
        except UnicodeDecodeError:
            continue
        ykr_id = str(traveltime_filepath)[-11:-4]
        print(f"YKR_ID: {ykr_id}")
        for mode in config.TRAVEL_MODES:
            tt_grid = get_grid_with_traveltimes(grid, traveltimes, mode)
            catchments = dissolve_grid_to_catchments(
                tt_grid, breakpoints=config.TIMES, mode=mode
            )
            catchments.to_file(
                Path(write_path / f"{2018}_{mode}_{ykr_id}.geojson"),
                driver="GeoJSON"
            )
            print(f"processed {mode}")


def get_paths_from_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--read_path", type=str)
    parser.add_argument("-w", "--write_path", type=str)
    args = parser.parse_args()
    read_path = args.read_path
    write_path = args.write_path
    return Path(read_path), Path(write_path)


def preprocess_grid(grid):
    """Reprojects the grid and discards unneeded data.

    This means rounding all coordinates to 5 decimal places and removing crs
    information after reprojection. The goal is to keep geojson size as small
    as possible.
    """
    def round_coords(feature):
        rounded_wkt = wkt.dumps(feature, rounding_precision=5)
        return wkt.loads(rounded_wkt)
    processed = grid.copy()
    processed = processed.to_crs(epsg=4326)
    processed.crs = None
    processed["geometry"] = processed["geometry"].apply(round_coords)
    return processed


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

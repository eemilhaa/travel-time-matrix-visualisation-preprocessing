"""A script for producing catchment polygons in geojson format."""
import argparse
from pathlib import Path
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

import geopandas as gpd
import pandas as pd
import numpy as np

from config import BREAKPOINTS, TRAVEL_MODES
from minify_geodataframe import minify_geodataframe
from logger import LOGGER
from minify_geojson import minify_files_in_dir


def main() -> None:
    user_args = _get_args()
    try:
        grid = gpd.read_file(user_args.grid_path)[["YKR_ID", "geometry"]]
    except KeyError:
        grid = gpd.read_file(user_args.grid_path)[["id", "geometry"]]
    grid = minify_geodataframe(grid, epsg=4326, coordinate_precision=5)

    filetype = "txt"
    matrix_paths = list(user_args.matrix_dir.rglob("*.txt"))
    if len(matrix_paths) < 13000:
        filetype = "csv"
        matrix_paths = list(user_args.matrix_dir.rglob("*.csv"))

    args = [(matrix_path, grid, user_args, filetype) for matrix_path in matrix_paths]
    process_parallel(args=args)
    minify_files_in_dir(user_args.write_dir)


def process_parallel(args: list) -> None:
    """Process matrices in parallel.

    Args:
        args: A list of tuples. Each tuples gets passed to process_matrix().
    """
    cpus = cpu_count()
    results = ThreadPool(cpus - 1).imap_unordered(process_matrix, args)
    for result in results:
        if result:
            LOGGER.info(f"    saved output to {result}")


def process_matrix(args: tuple) -> list | None:
    matrix_path, grid, user_args, filetype = args
    ykr_id = get_ykr_id_from_path(matrix_path)
    if not ykr_id:
        return None
    matrix = read_matrix_to_df(matrix_path, filetype)
    if type(matrix) != pd.DataFrame:
        return None
    LOGGER.info(f"Processing YKR_ID {ykr_id}")
    results = []
    for mode in TRAVEL_MODES:
        tt_grid = merge_traveltimes_to_grid(grid, matrix, mode)
        catchments = dissolve_grid_to_catchments(
            tt_grid, breakpoints=BREAKPOINTS, mode=mode
        )
        write_path = write_catchments_to_geojson(
            catchments, user_args.year, mode, ykr_id, user_args.write_dir
        )
        results.append(write_path)
        LOGGER.info(f"    processed {ykr_id}, {mode}")
    return results


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--grid_path", type=Path, required=True)
    parser.add_argument("-m", "--matrix_dir", type=Path, required=True)
    parser.add_argument("-w", "--write_dir", type=Path, required=True)
    parser.add_argument("-y", "--year", type=int, required=True)
    args = parser.parse_args()
    return args


def get_ykr_id_from_path(path: Path) -> str | None:
    """Gets the ykr id from a file path.

    Assumes that the id is the last thing in the file name. For example:
    travel_times_to_5785640.txt
    """
    ykr_id = str(path)[-11:-4]
    try:
        int(ykr_id)
    except ValueError:
        LOGGER.warning(f"No ykr_id found from: {path}")
        return None
    return ykr_id


def read_matrix_to_df(path: Path, filetype: str) -> pd.DataFrame | None:
    """Reads a matrix txt file into a df

    Additionally performs some simple checks on the file and the df so only a
    valid df is returned.
    """
    sep = ";"
    if filetype == "csv":
        sep = ","
    try:
        matrix = pd.read_csv(path, sep=sep, na_values=["-1"])
    except UnicodeDecodeError as e:
        LOGGER.warning(f"Read an inccompatible file: {path}\n({e})")
        return None
    if "from_id" not in matrix.columns:
        LOGGER.warning(
            f"from_id column missing from: {path}.\nMoving to next file."
        )
        return None
    return matrix


def merge_traveltimes_to_grid(
    grid: gpd.GeoDataFrame,
    traveltimes: pd.DataFrame,
    mode: str
) -> gpd.GeoDataFrame:
    """Merges a travel mode's traveltimes to a grid based on ykr_id"""

    intrest_times = traveltimes[["from_id", mode]]
    try:
        tt_grid = grid.merge(intrest_times, left_on="id", right_on="from_id")
    except:
        tt_grid = grid.merge(intrest_times, left_on="YKR_ID", right_on="from_id")
    tt_grid = tt_grid[["geometry", mode]]
    return tt_grid


def dissolve_grid_to_catchments(
    tt_grid: gpd.GeoDataFrame,
    breakpoints: list,
    mode: str,
) -> gpd.GeoDataFrame:
    """Makes the catchment polygons.

    This is done by iterating over the breakpoint values. Each cell gets
    assigned the smallest breakpoint value within which it can be reached. This
    value is stored in the column "t". After all breakpoints are checked, the
    grid is dissolved based on column "t".
    """
    tt_grid["t"] = np.NaN
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
    write_path = Path(write_dir/ filename)
    gdf.to_file(write_path, driver="GeoJSON")
    return write_path


if __name__ == "__main__":
    main()

"""A script for processing the ykr grid into a minimal geojson."""
import argparse
from pathlib import Path

import geopandas as gpd

from logger import LOGGER
from minify_geodataframe import minify_geodataframe
from minify_geojson import minify_file


def main() -> None:
    args = get_args()
    try:
        grid = gpd.read_file(args.read_path)[["YKR_ID", "geometry"]]
    except KeyError:
        grid = gpd.read_file(args.read_path)[["id", "geometry"]]
    grid = minify_geodataframe(grid, epsg=4326, coordinate_precision=5)
    write_path = Path(args.write_dir / "grid.geojson")
    grid.to_file(write_path, driver="GeoJSON")
    minify_file(write_path)
    LOGGER.info(f"Wrote grid geojson to {write_path}")


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--read_path", type=Path, required=True)
    parser.add_argument("-w", "--write_dir", type=Path, required=True)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()

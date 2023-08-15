import argparse
from pathlib import Path

from shapely import wkt
import geopandas as gpd

from minify_geojson import minify_file


def main():
    args = get_args()
    grid = gpd.read_file(args.read_path)[["YKR_ID", "geometry"]]
    grid = preprocess_grid(grid)
    write_path = Path(args.write_dir / "grid.geojson")
    grid.to_file(write_path, driver="GeoJSON")
    minify_file(write_path)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--read_path", type=Path, required=True)
    parser.add_argument("-w", "--write_dir", type=Path, required=True)
    args = parser.parse_args()
    return args


def preprocess_grid(grid):
    """Reprojects the grid and discards unneeded data.

    This means setting coordinate precision to 5 decimal places and removing
    crs information after reprojection. The goal is to keep geojson size as
    small as possible.
    """
    def round_coords(feature):
        rounded_wkt = wkt.dumps(feature, rounding_precision=5)
        return wkt.loads(rounded_wkt)
    processed = grid.copy()
    processed = processed.to_crs(epsg=4326)
    processed.crs = None
    processed["geometry"] = processed["geometry"].apply(round_coords)
    return processed


if __name__ == "__main__":
    main()

from pathlib import Path

import geopandas as gpd


def main():
    grid = gpd.read_file("./data/grid/")[["YKR_ID", "geometry"]]
    grid = grid.to_crs(epsg=4326)
    grid.to_file(Path("data/grid/grid.geojson", driver="GeoJSON"))


if __name__ == "__main__":
    main()

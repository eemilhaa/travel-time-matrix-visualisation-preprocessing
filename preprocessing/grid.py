from shapely import wkt
import geopandas as gpd


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

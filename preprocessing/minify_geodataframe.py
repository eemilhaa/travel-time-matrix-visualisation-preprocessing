import geopandas as gpd
from shapely import wkt


def minify_geodataframe(
    gdf: gpd.GeoDataFrame,
    epsg: int,
    coordinate_precision: int,
) -> gpd.GeoDataFrame:
    """Reprojects, simplifies coordinates and removes crs info from a gdf

    This function deals only with the geometry column and coordinates. Other
    simplifications should be done elsewhere.
    """
    def round_coords(feature):
        rounded_wkt = wkt.dumps(
            feature, rounding_precision=coordinate_precision
        )
        return wkt.loads(rounded_wkt)
    processed = gdf.copy()
    processed = processed.to_crs(epsg=4326)
    processed["geometry"] = processed["geometry"].apply(round_coords)
    processed.crs = None
    return processed

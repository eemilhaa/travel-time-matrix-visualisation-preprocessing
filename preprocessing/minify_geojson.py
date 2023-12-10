"""A module for doing the last bits of size optimisation on geojson files.

This means stripping whitespace and newlines used by GeoPandas when writing to
geojson. All other simplification (setting coordinate precision, setting data
types, removing unneeded fields etc.) should be done before writing to a file.
"""
from pathlib import Path
import json

from logger import LOGGER


def minify_files_in_dir(directory: Path, logging: bool=True):
    """Minifies all geojson files in a directory, in place."""

    for file_path in directory.rglob("*.geojson"):
        minify_file(file_path)
        if logging:
            LOGGER.info(f"Minified {file_path}")


def minify_file(file_path: Path):
    """Removes all whitespace and newlines from a geojson file, in place."""

    with open(file_path, "r") as openfile:
        json_object = json.load(openfile)
    minified = _minify_json_object(json_object)
    with open(file_path, "w") as outfile:
        outfile.write(minified)


def _minify_json_object(json_object):
    minified = json.dumps(json_object, separators=(',', ':'))
    return minified

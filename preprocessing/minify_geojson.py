from pathlib import Path
import json


def minify_files_in_dir(directory: Path):
    """Minifies all geojson files in a directory, in place."""

    for file_path in directory.rglob("*.geojson"):
        minify_file(file_path)


def minify_file(file_path: Path):
    """Removes all whitespace and newlines from a geojson file, in place."""

    with open(file_path, "r") as openfile:
        json_object = json.load(openfile)
    minified = json.dumps(json_object, separators=(',', ':'))
    with open(file_path, "w") as outfile:
        outfile.write(minified)
    print(f"Minified {file_path}")

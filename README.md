# TTM-preprocessing
Python tools for generating geodata from travel time matrices.
See this [backend](https://github.com/DigitalGeographyLab/travel-time-matrix-visualisation-backend)
for serving the data.

## Overview
### Features
- Generate travel time catchment polygons in geojson format
from TTM .txt files and YKR grid geodata
- Produce a geojson file of the YKR grid
- Simplification for geodataframes and geojsons -> minimal file sizes

### How the catchments are made
Catchments are produced for each YKR grid cell / travel mode combination.
The data is classified into catchments based on breakpoints
(values of travel time in minutes).
For example, if using breakpoints of `[15, 30, 60]`,
the result geojsons will have three (multi)polygons:
- Area with `traveltime <= 15`
- Area with `15 < traveltime <= 30`
- Area with `30 < traveltime <= 60`

### File sizes
File sizes are kept as small as possible. In practice this means:

At the geodataframe level:
- Removing the unneeded information (such as extra columns, crs info)
- Simplifying the needed information (such as coordinate precision)

At the file level:
- Removing all whitespace from the geojson objects written by geopandas

You should expect one processed matrix (all catchments for all travel modes)
to take up about 5GB of disk space.
This will of course vary based on the config used to generate the catchments.

## Setup
### Python
Make a virtual env:
```console
python -m venv venv && source venv/bin/activate
```
Install dependencies:
```console
pip install -r requirements.txt
```

### Data
You'll need:
- All of the .txt files that make up a travel time matrix
- The corresponding YKR grid

## Generating the files
### Catchmets
Optionally edit `preprocessing/config.py`
to include the travel modes and breakpoints you wish to use.

Generate the catchments with:
```console
python preprocessing/catchments.py \
  -g <directory/with/ykr-grid> \
  -m <directory/with/matrix/files> \
  -w <directory/to/write/catchments/to> \
  -y <year/to/tag/output/files/with>
```
The amount of time this takes depends on your hardware,
but be prepared for at least a few hours.
Progress is logged to the terminal.

### Grid
Generate the grid with:
```console
python preprocessing/grid.py \
  -r <path/to/ykr-grid> \
  -w <directory/to/write/grid/to>
```
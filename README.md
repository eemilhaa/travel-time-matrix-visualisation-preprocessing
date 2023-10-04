# TTM-preprocessing
Tools for producing geodata from travel time matrix text / csv files.
See this [backend](https://github.com/DigitalGeographyLab/travel-time-matrix-visualisation-backend)
for serving the data.

## Overview
### Features
- Generate travel time catchment polygons in geojson format
from TTM .txt / .csv files and YKR grid geodata
- Produce a minimal geojson file of the YKR grid
- Simplify geodataframes and geojsons, gzip everything -> lighter computation, minimal file sizes

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
File sizes are kept as small as possible by:

At the geodataframe level:
- Removing the unneeded information (such as extra columns, crs info)
- Simplifying the needed information (such as coordinate precision)

At the file level:
- Removing all whitespace from the geojson objects written by geopandas
- Gzipping everything

You should expect one processed matrix (all catchments for all travel modes)
to take up about 2.5GB of disk space.
This will of course vary based on the config used to generate the catchments.

## Tools and dependencies
### Python
Make a virtual env:
```console
python -m venv venv 
```
and activate it:
```console
source venv/bin/activate
```
Install dependencies:
```console
pip install -r requirements.txt
```

### Bash / gzip
Bash and gzip are necessary for compressing the files.
If you are on a unix-based system,
you probably have both and everything should just work.
If you are on windows,
the easiest thing to do is probably to run a linux container.
So, you'll need docker.

## Input data
You'll need:
- All of the .txt files that make up a travel time matrix
- The corresponding YKR grid

## Processing the data
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

### Compression
**Unix-based**:

Make the `compress` script executable and run it.
Give the path to the directory containing the files you want to compress as the only argument.
```console
./compress <path/to/data_directory>
```

**Windows**:

I do not know what the best way to do anything on windows would be,
but this should get you a workable environment:
```console
docker run -it --rm -v ./:/home ubuntu:latest
cd home
```

After that, follow the unix-based instructions.

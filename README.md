# TTM-preprocessing
Currently this is just a python script for transforming TTM data (.txt files)
to travel time catchment polygons in geojson format.

## What it does
Catchments are produced for each YKR grid cell / travel mode combination.
The data is classified into catchments based on breakpoints (values of travel time in minutes).
For example, if using breakpoints of `[15, 30, 60]`, the result geojson will have three (multi)polygons:
one for the area with `traveltime <= 15`, one for `15 < traveltime <= 30`, one for `30 < traveltime <= 60`.

## Setup
```console
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```
## Processing a matrix
Edit `preprocessing/config.py` to include the travel modes and breakpoints you wish to use.

Run:
```console
python preprocessing/catchments.py -r <path/to/matrix/files> -w <directory/to/write/catchments/to>
```
For example:
```console
python preprocessing/catchments.py -g data/grid -m data/HelsinkiTravelTimeMatrix2018 -w data/catchments -y 2018
```
to process a matrix. This will take a few hours depending on your hardware.

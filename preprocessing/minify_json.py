from pathlib import Path
import json

for f in Path("./data/catchments/").rglob("*.geojson"):
    print(f)
    with open(f, "r") as openfile:
        json_object = json.load(openfile)

    minified = json.dumps(json_object, separators=(',', ':'))
    with open(f, "w") as outfile:
        outfile.write(minified)
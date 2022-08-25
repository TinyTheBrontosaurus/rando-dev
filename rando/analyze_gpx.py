# Eastern States 100
# Creating visualizations to performance
# TODO
#  [ ] Load gpx
#  [ ] Load aid station locations
#  [ ] Add a gpx-to-something-faster quick loader
#  [ ] Measure time in aid stations & time to finish
#  [ ] Plot time in aid stations; compare to crewed aid stations
#  [ ] Measure % of time in aid stations
#  [ ] Make ^^^ Configurable, including position error for aid stations
#  [ ] Try to automatically calculate entrance/exit criteria at aid stations
#  [ ] Plot time between aid stations

# Major rev. hill EDA
#  [ ] Break up by vert gradient segments
#  [ ] Plot by vert gradient segments
#  [ ] Do some EDA on ^^^

# Major rev. make it official
#  [ ] Load in a "reference" gpx
#  [ ] Cast one gpx onto another / stretch distance between aid stations
#  [ ] Make sure it still works with the previous versions

# Major rev. share it
#  [ ] See if anyone else wants this

# Major major rev. Eff it we're doing it live
#  [ ] redo it all in JS and React.
#  [ ] put on a phone with live GPS.
#  [ ] Live logging.
#  [ ] Live sharing w/ intermittent connections
#  [ ] Audio cues. halfway to aid station. off trail. wrong way.


import sys
import argparse
from pathlib import Path
from rando import draw_gpx
import gpxpy
import gpxpy.gpx
from rando import definitions
import matplotlib.pyplot as plt
import numpy as np
from scipy import spatial, signal
from natsort import natsorted
import geopy.distance
from dataclasses import dataclass
from loguru import logger
import pickle

def load_gpx_from_cache(file: Path):
    """
    Load a GPX file. If it's not in the cache, the load it before picking it to cache.
    If it is in cache, just load the pickle'd version. About 5-10x faster
    :param file: The file to open
    :return: Parsed GPX
    """
    cache_filename: Path = definitions.CACHE_DIR / (file.name + ".cache")
    if not cache_filename.exists():
        # Load the file
        logger.info("Cache miss {filename}", filename=str(file))
        with file.open('r') as f:
            gpx = gpxpy.parse(f)
        logger.info("Filling cache")
        definitions.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with cache_filename.open("wb") as f:
            pickle.dump(gpx, f)

    else:
        logger.info("Cache hit {filename}", filename=str(file))
        with cache_filename.open("rb") as f:
            gpx = pickle.load(f)
    return gpx


def main(argv):
    parser = argparse.ArgumentParser(description="Ultramarathon analysis script")

    parser.add_argument("actual_race", type=Path, help="Path to GPX file of the race to analyze")
    parser.add_argument("aid_stations", type=Path, help="Path to GPX file for the aid station locations")

    args = parser.parse_args(argv)

    gpx = load_gpx_from_cache(args.actual_race)
    race_track = draw_gpx.load_full_race(gpx)

    gpx = load_gpx_from_cache(args.aid_stations)
    aid_stations = draw_gpx.load_aid_stations_from_gpx(gpx)


    foo = 1
    pass


if __name__ == "__main__":
    main(sys.argv[1:])
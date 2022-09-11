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
import json
import datetime
from typing import List
from pathlib import Path
from dataclasses import dataclass
import numpy as np
import gpxpy
import gpxpy.gpx
from rando import definitions
from loguru import logger
from rando.draw_gpx import calculate_distance, AlongVertTrack


@dataclass
class Track:
    lat: np.array
    lon: np.array
    ele: np.array
    time: List[datetime.datetime]

    def get_along_vert_track(self):
        distance_between_points = calculate_distance(self.lat, self.lon)

        # Calculate the total distance to that point
        dists_total = []
        last = 0
        for dist in distance_between_points:
            dists_total.append(last + dist)
            last += dist

        return AlongVertTrack(along=np.array(dists_total),
                              vert=np.array(self.ele))


def load_gpx_from_cache(file: Path, force_load=False):
    """
    Load a GPX file. If it's not in the cache, the load it before picking it to cache.
    If it is in cache, just load the pickle'd version. About 5-10x faster
    :param file: The file to open
    :return: Parsed GPX
    """
    cache_filename: Path = definitions.CACHE_DIR / (file.name + ".cache")
    if force_load or not cache_filename.exists():
        # Load the file
        logger.info("Cache miss {filename}", filename=str(file))
        with file.open('r') as f:
            gpx = gpxpy.parse(f)
        logger.info("Filling cache")
        definitions.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        lats = [pt.latitude for pt in gpx.tracks[0].segments[0].points]
        lons = [pt.longitude for pt in gpx.tracks[0].segments[0].points]
        eles = [pt.elevation * 39. / 12 for pt in gpx.tracks[0].segments[0].points]
        times = [str(pt.time) for pt in gpx.tracks[0].segments[0].points]

        loaded = {
            "lat": lats,
            "lon": lons,
            "ele": eles,
            "time": times,
        }

        with cache_filename.open("w") as f:
            json.dump(loaded, f)

    else:
        logger.info("Cache hit {filename}", filename=str(file))
        with cache_filename.open("rb") as f:
            loaded = json.load(f)
    return loaded


def main(argv):
    parser = argparse.ArgumentParser(description="Ultramarathon analysis script")

    parser.add_argument("actual_race", type=Path, help="Path to GPX file of the race to analyze")
    parser.add_argument("aid_stations", type=Path, help="Path to GPX file for the aid station locations")
    parser.add_argument("--ignore-cache", action="store_true", help="Ignore the cache")

    args = parser.parse_args(argv)

    race_track_dict = load_gpx_from_cache(args.actual_race, force_load=args.ignore_cache)
    #race_track = draw_gpx.load_full_race(gpx)

    aid_stations_dict = load_gpx_from_cache(args.aid_stations, force_load=args.ignore_cache)
    #aid_stations = draw_gpx.load_aid_stations_from_gpx(gpx)

    pass


if __name__ == "__main__":
    main(sys.argv[1:])
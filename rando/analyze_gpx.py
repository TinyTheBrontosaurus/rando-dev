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
from rando.io import load_gpx_from_cache


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
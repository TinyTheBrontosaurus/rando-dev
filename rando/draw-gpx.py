import sys
import gpxpy
import gpxpy.gpx
import pandas as pd
from rando import definitions
import matplotlib.pyplot as plt


def main(_argv):
    gpxfile = definitions.DATA_DIR / "Eastern_States_100_Course_2021.gpx"
    with gpxfile.open('r') as f:
        gpx = gpxpy.parse(f)

    lats = [pt.latitude for pt in gpx.tracks[0].segments[0].points]
    lons = [pt.longitude for pt in gpx.tracks[0].segments[0].points]
    eles = [pt.elevation * 39./12 for pt in gpx.tracks[0].segments[0].points]

    plt.plot(eles)
    plt.show()
    pass



if __name__ == "__main__":
    main(sys.argv[1:])
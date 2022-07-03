import sys
import gpxpy
import gpxpy.gpx
import pandas as pd
from rando import definitions
import matplotlib.pyplot as plt
import numpy as np
from scipy import spatial
from natsort import natsorted


def main(_argv):
    gpxfile = definitions.DATA_DIR / "Eastern_States_100_Course_2021.gpx"
    with gpxfile.open('r') as f:
        gpx = gpxpy.parse(f)

    lats = [pt.latitude for pt in gpx.tracks[0].segments[0].points]
    lons = [pt.longitude for pt in gpx.tracks[0].segments[0].points]
    eles = [pt.elevation * 39./12 for pt in gpx.tracks[0].segments[0].points]

    wplats = [pt.latitude for pt in gpx.waypoints]
    wplons = [pt.longitude for pt in gpx.waypoints]
    wpnams = [pt.comment for pt in gpx.waypoints]

    nplats = np.array(lats)
    nplons = np.array(lons)

    A = np.stack((nplats, nplons)).transpose()

    wpdims = []
    for wplat, wplon, wpnam in zip(wplats, wplons, wpnams):
        pt = (wplat, wplon)
        _distance, idx = spatial.KDTree(A).query(pt)
        wpdims.append(idx)

    wpdims, wpnams = parallel_sort(wpdims, wpnams)

    last = 0
    last_title = "START"
    count = 0
    stats_all = calc_stats(eles)
    for dim, title in zip(wpdims, wpnams):
        plt.figure()
        local_ele = eles[last:dim]
        stats_local = calc_stats(local_ele)

        ax = plt.plot(local_ele)
        plt.title(f"{last_title} to {title}")
        plt.xlabel(f"{round(stats_local['up'], -1):.0f}ft up; {round(stats_local['down'], -1):.0f}ft down")
        plt.ylabel("Elevation (ft)")
        plt.ylim([500, 2200])
        frame1 = plt.gca()
        frame1.axes.xaxis.set_ticklabels([])
        plt.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        last = dim
        last_title = title
        count += 1
        if count > 1:
            #break
            pass

    plt.show()

    pass

def calc_stats(elevations):
    last = elevations[0]
    up = 0
    down = 0
    for el in elevations:
        if el < last:
            # going down
            down += last - el
        else:
            up += el - last
        last = el

    return {"down": down, "up": up}

def parallel_sort(X, Y):
    x_sorted = [x for _, x in natsorted(zip(Y, X))]
    y_sorted = natsorted(Y)
    return x_sorted, y_sorted


#    plt.plot(eles)
#    plt.show()
    pass



if __name__ == "__main__":
    main(sys.argv[1:])
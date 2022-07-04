# Eastern States 100
# Creating visualizations to show the vert between aid stations

import sys
import gpxpy
import gpxpy.gpx
from rando import definitions
import matplotlib.pyplot as plt
import numpy as np
from scipy import spatial
from natsort import natsorted
import geopy.distance



# TODO
#  [x] Plot elevations vs index
#  [x] Plot elevations vs distance
#  [x] Break up and label aid station to aid station
#  [x] Label distance up vs down
#  [x] Label # of miles
#  [x] Save to PNG
#  [x] Save on phone
#  [x] Adjust for readability on phone (1)
# (^^ as of v0.0.1)
#  [] Increase fonts for phone (2)
#  [] Annotate the grade of each hill
#  [] Post on reddit

def main(_argv):
    gpxfile = definitions.DATA_DIR / "Eastern_States_100_Course_2021.gpx"
    with gpxfile.open('r') as f:
        gpx = gpxpy.parse(f)

    # Load track's the lat, lon, and elevation
    lats = [pt.latitude for pt in gpx.tracks[0].segments[0].points]
    lons = [pt.longitude for pt in gpx.tracks[0].segments[0].points]
    eles = [pt.elevation * 39./12 for pt in gpx.tracks[0].segments[0].points]
    # Calculate distances between each point
    dists_rel = calculate_distance(lats, lons)
    # Calculate the total distance to that point
    dists_total = []
    last = 0
    for dist in dists_rel:
        dists_total.append(last + dist)
        last += dist

    # Load the waypoints
    wplats = [pt.latitude for pt in gpx.waypoints]
    wplons = [pt.longitude for pt in gpx.waypoints]
    wpnams = [pt.comment for pt in gpx.waypoints]

    # Convert to a numpy matrix of lats/lons
    nplats = np.array(lats)
    nplons = np.array(lons)
    latlons = np.stack((nplats, nplons)).transpose()

    # Calculate the index into the track arrays for each waypoint. That is, the closest lat/lon
    # corresponding to that waypoint's lat/lon
    wpdims = []
    for wplat, wplon, wpnam in zip(wplats, wplons, wpnams):
        pt = (wplat, wplon)
        _distance, idx = spatial.KDTree(latlons).query(pt)
        wpdims.append(idx)

    wpdims, wpnams = parallel_sort(wpdims, wpnams)

    last = 0
    last_title = "START"
    count = 0
    stats_all = calc_stats(eles)
    full_el_range_low = round(min(eles), -2) - 100
    full_el_range_high = round(max(eles), -2) + 100
    full_el_range = full_el_range_high - full_el_range_low
    out_folder = definitions.ROOT_DIR / "out"
    out_folder.mkdir(parents=True, exist_ok=True)
    for dim, title in zip(wpdims, wpnams):
        local_ele = eles[last:dim]
        local_dist = dists_total[last:dim]
        stats_local = calc_stats(local_ele)
        marker_start = local_dist[0]
        marker_end = local_dist[-1]
        length = marker_end - marker_start

        local_dist_rel = np.array(local_dist) - min(local_dist)

        # Plot it
        aid_station_label = f"{last_title}\nto\n{title}"
        miles_label = f"{length:.1f} miles\n{marker_start:.1f} mi to {marker_end:.1f} mi"
        elevation_label = f"{round(stats_local['up'], -1):.0f}ft climb; {round(stats_local['down'], -1):.0f}ft descent"
        plt.figure(figsize=(4, 6), dpi=80)
        plt.plot(local_dist_rel, local_ele)
        plt.title(f"{aid_station_label}")
        plt.xlabel(f"{miles_label}")
        plt.ylabel(f"Elevation (ft); {elevation_label}")
        plt.xticks(np.arange(0, round(length) + 1))
        plt.tick_params(axis="x", direction="in")
        plt.ylim([full_el_range_low, full_el_range_high])
        plt.yticks(rotation=90)
        frame1 = plt.gca()
        frame1.axes.xaxis.set_ticklabels([])
        plt.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=True,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        outfile = out_folder / f"{title}.png"
        plt.savefig(str(outfile))

        # Clean up
        last = dim
        last_title = title
        count += 1
        if count > 1:
            #break
            pass

    #plt.show()

    pass


def calc_stats(elevations) -> dict:
    """
    Calculate basic statistics given an elevation curve
    :param elevations: Array of elevations
    :return: Dictionary of stats
    """
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
    """
    Sort two parallel arrays (X & Y) by one of the arrays (Y)
    :param X:
    :param Y:
    :return: Both, sorted by Y
    """
    x_sorted = [x for _, x in natsorted(zip(Y, X))]
    y_sorted = natsorted(Y)
    return x_sorted, y_sorted


def calculate_distance(lats, lons) -> list:
    distances = [0]
    last_lat = lats[0]
    last_lon = lons[0]

    for lat, lon in zip(lats, lons):
        distances.append(geopy.distance.geodesic((lat, lon), (last_lat, last_lon)).miles)
        last_lat = lat
        last_lon = lon

    return distances


if __name__ == "__main__":
    main(sys.argv[1:])
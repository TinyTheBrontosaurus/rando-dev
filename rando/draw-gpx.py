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
#  [x] Post on reddit
#  [x] Use custom waypoints (not build into gpx like ES100)
#  [x] Do & post VT 100
# (^^ as of v0.0.2)
#  [] Increase fonts for phone (2)
#  [] Annotate the grade of each hill

VT100 = (
    ("AS1 Densmore Hill", 7.0),
    ("AS2 Dunham Hill", 11.5),
    ("AS3 Taftsville Bridge	", 14.4),
    ("AS4 So. Pomfret", 17.5),
    ("AS5 Pretty House", 21.2),
    ("AS6 U-Turn", 25.3),
    ("AS7 Stage Rd", 30.5),
    ("AS8 Route 12", 33.5),
    ("AS9 Lincoln Covered Bridge", 38.3),
    ("AS9a Barr House", 41.4),
    ("AS10 Lillians", 44.3),
    ("AS11 Camp 10 Bear", 47.4),
    ("AS12 Pinky's", 51.5),
    ("AS13 Birminghams", 54.0),
    ("AS14 Margaritaville", 58.7),
    ("AS15 Puckerbrush", 61.7),
    ("AS16 Brown School House", 64.6),
    ("AS17 Camp 10 Bear", 69.4),
    ("AS18 Seabrook", 74.1),
    ("AS19 Spirit of 76", 76.5),
    ("AS20 Goodman's", 80.5),
    ("AS21 Cow Shed", 83.2),
    ("AS22 Bill's", 88.2),
    ("AS23 Keating's", 92.5),
    ("AS24 Polly's", 94.5),
    ("FINISH LINE", 100)
)
infilename = "Vermont_100.gpx"
custom_waypoints = VT100

# infilename = "Eastern_States_100_Course_2021.gpx"
# custom_waypoints = False




def main(_argv):
    gpxfile = definitions.DATA_DIR / infilename
    with gpxfile.open('r') as f:
        gpx = gpxpy.parse(f)

    subfolder_name = gpxfile.stem

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

    if not custom_waypoints:
        waypoints = load_waypoints_from_gpx(gpx, lats, lons)
        wpdims, wpnams = parallel_sort(*waypoints)
    else:
        wpdims, wpnams = load_waypoints_by_distance(dists_total, custom_waypoints)


    last = 0
    last_title = "START"
    count = 0
    stats_all = calc_stats(eles)
    full_el_range_low = round(min(eles), -2) - 100
    full_el_range_high = round(max(eles), -2) + 100
    full_el_range = full_el_range_high - full_el_range_low
    out_folder = definitions.ROOT_DIR / "out" / subfolder_name
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
        if count > 25:
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
    distances = []
    last_lat = lats[0]
    last_lon = lons[0]

    for lat, lon in zip(lats, lons):
        distances.append(geopy.distance.geodesic((lat, lon), (last_lat, last_lon)).miles)
        last_lat = lat
        last_lon = lon

    return distances


def load_waypoints_from_gpx(gpx, lats, lons):
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

    return wpdims, wpnams

def load_waypoints_by_distance(dists_total, aid_stations):
    as_names = [x[0] for x in aid_stations]
    as_distances = [x[1] for x in aid_stations]
    wpdims = np.searchsorted(dists_total, as_distances, side='left', sorter=None)

    return wpdims, as_names

if __name__ == "__main__":
    main(sys.argv[1:])
# Eastern States 100
# Creating visualizations to show the vert between aid stations

import sys
import gpxpy
import gpxpy.gpx
from rando import definitions
import matplotlib.pyplot as plt
import numpy as np
from scipy import spatial, signal
from natsort import natsorted
import geopy.distance
from dataclasses import dataclass


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


# Lazy configs
count_to_show = 2
show = True
race = "Canyons 100k 2023"


# Races
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

if race == "VT100_strava":
    infilename = "Vermont_100.gpx"
    custom_aid_stations = VT100
elif race == "VT100_garmin":
    infilename = "COURSE_22875310.gpx"
    custom_aid_stations = VT100
elif race == "ES100":
    infilename = "Eastern_States_100_Course_2021.gpx"
    custom_aid_stations = False
elif race == "Leadville":
    infilename = "Leadville_100_Run.gpx"
    custom_aid_stations = False
elif race == "Canyons 100k 2023":
    infilename ="2023_Canyons_100k_V2_b5zvzd.gpx"
    custom_aid_stations = False
else:
    raise ValueError(f"Unknown race: {race}")


@dataclass
class Track:
    along: np.array
    vert: np.array

    @property
    def stats(self):
        return calc_stats(self.vert)

    @property
    def vert_max(self):
        return round(max(self.vert), -2) - 100

    @property
    def vert_min(self):
        return round(min(self.vert), -2) - 100

    @property
    def vert_range(self):
        return self.vert_max - self.vert_min

    def get_segment(self, fromi, toi):
        return Track(along=self.along[fromi:toi], vert=self.vert[fromi:toi])

    @property
    def start(self):
        return self.along[0]

    @property
    def end(self):
        return self.along[-1]

    @property
    def length(self):
        return self.end - self.start

    @property
    def along_local(self):
        return self.along - self.along[0]


def main(_argv):
    gpxfile = definitions.DATA_DIR / infilename
    with gpxfile.open('r') as f:
        gpx = gpxpy.parse(f)

    subfolder_name = gpxfile.stem

    full_race = load_full_race(gpx)

    # Load the aid stations (as)
    if not custom_aid_stations:
        aid_stations = load_aid_stations_from_gpx(gpx)
        asis, asnames = parallel_sort(*aid_stations)
    else:
        asis, asnames = load_aid_stations_by_distance(full_race.along, custom_aid_stations)


    # as => aid station
    last_asi = 0
    last_as_title = "START"
    count = 0
    out_folder = definitions.ROOT_DIR / "out" / subfolder_name
    out_folder.mkdir(parents=True, exist_ok=True)
    for asi, as_title in zip(asis, asnames):
        # Grab the segment
        segment = full_race.get_segment(last_asi, asi)

        # Create labels
        aid_station_label = f"{last_as_title}\nto\n{as_title}"
        miles_label = f"{segment.length:.1f} miles\n{segment.start:.1f} mi to {segment.end:.1f} mi"
        elevation_label = f"{round(segment.stats['up'], -1):.0f}ft climb; {round(segment.stats['down'], -1):.0f}ft descent"
        # Plot it
        plt.figure(figsize=(4, 6), dpi=80)
        plt.plot(segment.along_local, segment.vert)

        # Fancy up the axes
        plt.title(f"{aid_station_label}")
        plt.xlabel(f"{miles_label}")
        plt.ylabel(f"Elevation (ft); {elevation_label}")
        plt.xticks(np.arange(0, round(segment.length) + 1))
        plt.tick_params(axis="x", direction="in")
        plt.ylim([full_race.vert_min, full_race.vert_max])
        plt.yticks(rotation=90)
        frame1 = plt.gca()
        frame1.axes.xaxis.set_ticklabels([])
        plt.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=True,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off

        # Save to file
        outfile = out_folder / f"{as_title}.png"
        plt.savefig(str(outfile))

        # Clean up
        last_asi = asi
        last_as_title = as_title
        count += 1
        if count >= count_to_show and show:
            break

    if show:
        plt.show()


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


def load_aid_stations_from_gpx(gpx):
    lats = [pt.latitude for pt in gpx.tracks[0].segments[0].points]
    lons = [pt.longitude for pt in gpx.tracks[0].segments[0].points]

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

def load_aid_stations_by_distance(dists_total, aid_stations):
    as_names = [x[0] for x in aid_stations]
    as_distances = [x[1] for x in aid_stations]
    wpdims = np.searchsorted(dists_total, as_distances, side='left', sorter=None)

    return wpdims, as_names


def load_full_race(gpx):
    # Load track's the lat, lon, and elevation
    lats = [pt.latitude for pt in gpx.tracks[0].segments[0].points]
    lons = [pt.longitude for pt in gpx.tracks[0].segments[0].points]
    eles = [pt.elevation * 39. / 12 for pt in gpx.tracks[0].segments[0].points]

    distance_between_points = calculate_distance(lats, lons)

    # Calculate the total distance to that point
    dists_total = []
    last = 0
    for dist in distance_between_points:
        dists_total.append(last + dist)
        last += dist

    return Track(along=np.array(dists_total),
                 vert=np.array(eles))


if __name__ == "__main__":
    main(sys.argv[1:])
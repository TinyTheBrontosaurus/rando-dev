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
count_to_show = 999
show = False
race = "Cruel Jewel 2024"


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

Canyons100k2023 = (
    ("01-HS1 No Hands 1", 3.5),
    ("02-AS1 Cool 1 (Crew)", 6.5),
    ("03-AS2 Cool 2 (Crew)", 14.3),
    ("04-AS3 Browns Bar 1", 18.5),
    ("05-AS4 ALT", 23.9),
    ("06-AS5 Browns Bar 2", 30.3),
    ("07-HS2 No Hands 2", 36.4),
    ("08-AS6 Mammoth Bar (Drop Bag)", 40.4),
    ("09-AS7 Drivers Flat (Crew)", 48.3),
    ("10-AS8 Clementine", 56.7),
    ("11-HS3 No Hands 3", 60.4),
    ("12-Downtown Auburn - Finish", 63.9)
)

TheRut50k2023 = (
    ("01-Moonlight Lodge 1", 5.6),
    ("02-Moonlight Lodge 2", 10.6),
    ("03-Swiftcurrent", 18.7),
    ("04-Dakota (Water Only", 21.7),
    ("05-Moosetracks", 24),
    ("06-Andesite", 26.2),
    ("07-FINISH", 31.1)
)

if race == "Cruel Jewel 2024":
    infilename = "2023-cruel-jewel-100-final.gpx"
    custom_aid_stations = (
        ("AS1 Deep Gap", 2.7),
        ("AS2 Deep Gap (Bib Punch)", 8.5),
        ("AS3 Stanley Gap", 13.2),
        ("AS4 Old Dial Road", 19.1),
        ("AS5 Wilscot Gap", 24.6),
        ("AS6 Skeenah Gap", 29.5),
        ("AS7 Fish Gap", 34.4),
        ("AS8 Fire Pit", 41.7),
        ("AS9 Wolf Creek", 46.4),
        ("AS10 Poor Decisions (Bib Punch)", 49.1),
        ("AS11 Wolf Creek", 51.8),
        ("AS12 Fire Pit", 56.5),
        ("AS13 Fish Gap", 63.8),
        ("AS14 Skeenah Gap", 68.7),
        ("AS15 Wilscot Gap", 73.6),
        ("AS16 Old Dial Road", 79.1),
        ("AS17 Stanley Gap", 85),
        ("AS18 Weaver Creek Road", 90.4),
        ("AS19 Deep Gap", 95.4),
        ("AS20 Deep Gap (Bib Punch)", 101.2),
        ("FINISH LINE", 107)
    )
elif race == "VT100_strava":
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
    infilename ="2023_Canyons_Endurance_Runs_by_UTMB_100k_new_Course_9ab992e1c7.gpx"
    custom_aid_stations = Canyons100k2023
elif race == "Ragged 75":
    infilename = ["Ragged_75_Stage_1.gpx", "Ragged_75_Stage_2.gpx", "Ragged_75_Stage_3.gpx"]
    S1 = 24.22
    S2 = 23.26
    S3 = 33.46
    custom_aid_stations = (
        ("01-AS1 ", S1/2),
        ("02-CKP Wadeligh State park", S1),
        ("03-AS1 ", S1 + S2/2),
        ("04-CKP Sunapee Middle School", S1 + S2),
        ("05-AS1 ", S1 + S2 + S3/6),
        ("06-AS2 ", S1 + S2 + 2*S3/6),
        ("07-AS3 ", S1 + S2 + 3*S3/6),
        ("08-AS4 ", S1 + S2 + 4*S3/6),
        ("09-AS5 ", S1 + S2 + 5*S3/6),
        ("10-Finish", float('inf')),
    )

elif race == "The Rut":
    infilename = "Rut_50k.gpx"
    custom_aid_stations = (
        ("01-AS1 Moonlight Lodge #1", 5.6),
        ("02-AS2 Moonlight Lodge #2", 10.6),
        ("03-AS3 Swiftcurrent", 18.7),
        ("04-HS1 Dakota", 21.7),
        ("05-AS4 Moosetracks", 24),
        ("06-AS5 Andesite", 26.2),
        ("Finish line", 31.04),
    )
elif race == "Crazy Mountain 100":
    infilename = "Crazy_Mountain_100.gpx"
    custom_aid_stations = (
        ("01 #1 Porcupine", 6),
        ("02 #2 Ibex", 19.3),
        ("03 #3 Cow Camp", 32),
        ("04 #4 Halfmoon", 43.6),
        ("05 *Conical pass cutoff", 50.4),
        ("06 #5 Cow Camp", 55.2),
        ("07 #6 Sunlight", 63.8),
        ("08 #7 Crandall", 69.7),
        ("09 #8 Forest Lake", 76.3),
        ("10 #9 Honey Trail", 88.7),
        ("11 #10 Huntin Camp", 95.8),
        ("12 Finish", 103),
    )
elif race == "The Rut 5k 2023":
    infilename = "2023 The Rut 50k.gpx"
    custom_aid_stations = TheRut50k2023
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
        return round(max(self.vert), -2) + 100

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
    if isinstance(infilename, str):
        files_list = [infilename]
    else:
        files_list = infilename

    lats = []
    lons = []
    full_race = None
    for gpxfilename in files_list:

        gpxfile = definitions.DATA_DIR / gpxfilename
        with gpxfile.open('r') as f:
            gpx = gpxpy.parse(f)

        subfolder_name = gpxfile.stem

        partial_race = load_full_race(gpx)
        lats.extend([pt.latitude for pt in gpx.tracks[0].segments[0].points])
        lons.extend([pt.longitude for pt in gpx.tracks[0].segments[0].points])

        if full_race is None:
            full_race = partial_race
        else:
            full_race.vert = np.append(full_race.vert, partial_race.vert)
            full_race.along = np.append(full_race.along, partial_race.along + full_race.along[-1])

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
    color = None
    for asi, as_title in zip(asis, asnames):
        # Grab the segment
        segment = full_race.get_segment(last_asi, asi)

        # Create labels
        aid_station_label = f"{last_as_title}\nto\n{as_title}"
        miles_label = f"{segment.length:.1f} miles\n{segment.start:.1f} mi to {segment.end:.1f} mi"
        elevation_label = f"{round(segment.stats['up'], -1):.0f}ft climb; {round(segment.stats['down'], -1):.0f}ft descent"

        color = None if color else 'lightgray'

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
        if color:
            ax = plt.gca()
            ax.set_facecolor(color)

        # Save to file
        outfile = out_folder / f"{as_title}.png"
        plt.savefig(str(outfile), facecolor=color)

        # Plot overhead
        #plt.figure(figsize=(4, 6), dpi=80)
        fig, axs = plt.subplots(2, 1, figsize=(4, 6), dpi=80, height_ratios=[4, 1])
        ax = axs[0]
        ax.plot(lons, lats, 'y')
        ax.plot(lons[last_asi:asi], lats[last_asi:asi], 'b')
        ax.plot(lons[last_asi], lats[last_asi], 'go')
        ax.plot(lons[asi-1], lats[asi-1], 'ro')
        ax.axis('square')
        ax.grid(False)
        ax.axis('off')
        ax.margins(0)

        ax = axs[1]
        ax.plot(full_race.along, full_race.vert, 'y')
        ax.plot(segment.along, segment.vert, 'b')

        # Fancy up the axes
        ax.grid(False)
        ax.axis('off')

        fig.suptitle(
            f"{last_as_title} to\n{as_title}\n"
            f"{segment.length:.1f} miles; {segment.start:.1f} mi to {segment.end:.1f} mi\n"
            f"{elevation_label}")#,
#            y=1, pad=-14, loc='left')

        # Save it
        outfile = out_folder / f"{as_title}-xy.png"
        plt.savefig(str(outfile), bbox_inches=0, facecolor=color)

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
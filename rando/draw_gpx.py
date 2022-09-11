# Eastern States 100
# Creating visualizations to show the vert between aid stations

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


import sys
import gpxpy
import gpxpy.gpx
from rando import definitions
import matplotlib.pyplot as plt
import numpy as np

from rando.io import load_aid_stations_from_gpx, load_full_race, load_aid_stations_by_distance
from rando.track import parallel_sort

# Lazy configs
count_to_show = 2
show = True
race = "ES100"


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
else:
    raise ValueError(f"Unknown race: {race}")



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




if __name__ == "__main__":
    main(sys.argv[1:])
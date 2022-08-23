# Eastern States 100
# Creating visualizations to performance

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
#  [ ] Load gpx
#  [ ] Load aid station locations
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

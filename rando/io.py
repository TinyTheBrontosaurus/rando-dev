import numpy as np
from scipy import spatial
import json
from pathlib import Path
import gpxpy
import gpxpy.gpx
from loguru import logger
from rando import definitions
from rando.track import calculate_distance, AlongVertTrack


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

    return AlongVertTrack(along=np.array(dists_total),
                          vert=np.array(eles))



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
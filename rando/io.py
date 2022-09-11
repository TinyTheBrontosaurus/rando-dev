import numpy as np
from scipy import spatial
from rando.track import AlongVertTrack, calculate_distance

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

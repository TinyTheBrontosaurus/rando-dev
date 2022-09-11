@dataclass
class AlongVertTrack:
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
        return AlongVertTrack(along=self.along[fromi:toi], vert=self.vert[fromi:toi])

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


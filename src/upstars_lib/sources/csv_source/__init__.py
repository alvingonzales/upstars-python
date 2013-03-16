
import csv
import os
from datetime import datetime
import threading

from upstars_lib.sky_objects import Star, Line
from upstars_lib.coordinates import calculate_bounds, within_bounds, RaDec
from upstars_lib.projectors import AzAltProjector

class _CsvSource:
    def __init__(self):
        csv_path = "ConstellationLinesAll2002.csv"
        if __name__ != "__main__":
            csv_path = os.path.join(os.path.dirname(__file__), csv_path)
        f = open(csv_path, "r")
        stars = {}
        lines = []
        try:
            constellations_csv = csv.reader(f)
            for _ in range(8):
                constellations_csv.next()

            previous_coords = None
            for row in constellations_csv:
                constellation_name = row[0]
                star_name = row[1]
                coords_ra = row[2]
                coords_dec = row[3]
                star_magnitude = row[4]

                current_coords = None
                if star_name:
                    star_id = "%s-%s" % (constellation_name, star_name)
                    current_coords = RaDec(float(coords_ra), float(coords_dec))
                    if star_id not in stars:
                        stars[star_id] = Star(star_id, star_name, current_coords, float(star_magnitude))

                if previous_coords and current_coords:
                    lines.append((previous_coords, current_coords))

                previous_coords = current_coords

        finally:
            f.close()

        self.stars = stars.values()
        self.lines = lines


    def get_sky_objects(self, zoom, x, y):
        bounds = calculate_bounds(zoom, x, y)
        (nw_ra, nw_dec, se_ra, se_dec) = bounds
        print "getting stars between %s and %s" % ((nw_ra, nw_dec), (se_ra, se_dec))

        found_stars = []
        for star in self.stars:
            if within_bounds(star.radec, bounds):
                found_stars.append(star)
#            else:
#                print star, " does not fit"
        for line in self.lines:
            coords1, coords2 = line
            if within_bounds(coords1, bounds) or within_bounds(coords2, bounds):
                found_stars.append(Line(coords1, coords2))

        return bounds, found_stars


_csvsource = None
_csvsource_lock = threading.Lock()
def CsvSource():
    global _csvsource
    _csvsource_lock.acquire()
    try:
        if not _csvsource:
            _csvsource = _CsvSource()
    finally:
        _csvsource_lock.release()

    return _csvsource


class _ProjectedCsvSource(_CsvSource):
    def __init__(self, year, month, date, hour, minute, longitude, latitude):
        _CsvSource.__init__(self)
        utc = datetime(year, month, date, hour, minute)
        self.projector = AzAltProjector(utc, (longitude, latitude))
        projected_stars = []
        #for star in self.stars:



def main():
    source = CsvSource()
    bounds, stars = source.get_sky_objects(3, 0, 2)
    print bounds
    for star in stars:
        print star


if __name__ == "__main__":
    main()

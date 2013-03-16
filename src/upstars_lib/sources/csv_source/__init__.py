
import csv
import os

from upstars_lib.sky_objects import Star, Line
from upstars_lib.coordinates import calculate_bounds, within_bounds

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
            for i in range(8):
                constellations_csv.next()

            previous_star = None
            for row in constellations_csv:
                constellation_name = row[0]
                star_name = row[1]
                coords_ra = row[2]
                coords_dec = row[3]
                star_magnitude = row[4]

                current_star = None
                if star_name:
                    star_id = "%s-%s" % (constellation_name, star_name)
                    current_star = Star(star_id, star_name, float(coords_ra), float(coords_dec), float(star_magnitude))
                    if star_id not in stars:
                        stars[star_id] = current_star

                if previous_star and current_star:
                    lines.append((previous_star, current_star))

                previous_star = current_star

        finally:
            f.close()

        self.stars = stars.values()
        self.lines = lines


    def get_stars(self, zoom, x, y):
        bounds = calculate_bounds(zoom, x, y)
        (nw_ra, nw_dec, se_ra, se_dec) = bounds
        print "getting stars between %s and %s" % ((nw_ra, nw_dec), (se_ra, se_dec))

        found_stars = []
        for star in self.stars:
            if within_bounds(star, bounds):
                found_stars.append(star)
#            else:
#                print star, " does not fit"
        for line in self.lines:
            star1, star2 = line
            if within_bounds(star1, bounds) or within_bounds(star2, bounds):
                found_stars.append(Line(star1, star2))

        return bounds, found_stars


_csvsource = None
def CsvSource():
    global _csvsource
    if not _csvsource:
        _csvsource = _CsvSource()

    return _csvsource


def main():
    source = CsvSource()
    bounds, stars = source.get_stars(3, 0, 2)
    print bounds
    for star in stars:
        print star


if __name__ == "__main__":
    main()

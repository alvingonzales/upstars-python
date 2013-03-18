
import csv
import os
from datetime import datetime
import threading

from upstars_lib.sky_objects import Star, Line
from upstars_lib.coordinates import calculate_bounds, within_bounds, RaDec, LonLat, AzAlt
from upstars_lib.projectors import AzAltProjector

class _CsvSource:
    def __init__(self):
        self.stars, self.lines = self.load_from_file()

    def load_from_file(self):
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
                    lines.append(Line(previous_coords, current_coords))

                previous_coords = current_coords

        finally:
            f.close()

        return stars.values(), lines


    def get_sky_objects(self, zoom, x, y):
        bounds = calculate_bounds(zoom, x, y)
        (nw_ra, nw_dec, se_ra, se_dec) = bounds

        found_stars = []
        for star in self.stars:
            if within_bounds(star.radec, bounds):
                found_stars.append(star)

        for line in self.lines:
            point1, point2 = line.point1, line.point2

            if within_bounds(point1, bounds) or within_bounds(point2, bounds):
                # fixes for wrap arounds
                if not within_bounds(point1, bounds):
                    point1 = fix_wrap_around(point2, point1)
                elif not within_bounds(point2, bounds):
                    point2 = fix_wrap_around(point1, point2)

                found_stars.append(Line(point1, point2))

            else:
                case1 = point1, fix_wrap_around(point1, point2)
                case2 = point2, fix_wrap_around(point2, point1)

                found = None
                for case in [case1, case2]:
                    found = check_if_line_goes_through(bounds, case)
                    if found:
                        break

                if found:
                    found_stars.append(found)


        return bounds, found_stars


def fix_wrap_around(fixed_point, point):
    if point.az < fixed_point.az:
        offset = 24.0
    else:
        offset = -24.0

    if abs(point.az + offset - fixed_point.az) < abs(point.az - fixed_point.az):
        point = AzAlt(point.az+offset, point.alt)

    return point


def check_if_line_goes_through(bounds, case):
    left, top, right, bottom = bounds
    (x1, y1), (x2, y2) = case
    a = (y1 - y2) / (x1 - x2)
    b = y2 - a * x2
    fx = lambda x:a * x + b
    fy = lambda y:(y - b) / a

    test_values = [
        (fx(left), top, bottom, y1, y2),
        (fx(right), top, bottom, y1, y2),
        (fy(top), right, left, x1, x2),
        (fy(bottom), right, left, x1, x2)
        ]

    found = None
    for test_value, upper, lower, limit1, limit2 in test_values:
        if (upper >= test_value and lower <= test_value
            and limit1 >= test_value and limit2 <= test_value):
            found = Line(*case)
            break

    return found


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
    def __init__(self, year, month, day, hour, minute, longitude, latitude):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.longitude = longitude
        self.latitude = latitude
        _CsvSource.__init__(self)


    def load_from_file(self):
        stars, lines = _CsvSource.load_from_file(self)

        utc = datetime(self.year, self.month, self.day, self.hour, self.minute)
        projector = AzAltProjector(utc, LonLat(self.longitude, self.latitude))
        projected_stars = []
        for star in stars:
            azalt = projector.project(star.radec)
            projected_stars.append(Star(star.id, star.name, azalt, star.mag))

        projected_lines = []
        for line in lines:
            point1 = projector.project(line.point1)
            point2 = projector.project(line.point2)
            projected_lines.append(Line(point1, point2))

        return projected_stars, projected_lines


_projected_csvsources = {}
_projected_csvsources_lock = threading.Lock()
def ProjectedCsvSource(year, month, date, hour, minute, longitude, latitude):
    _projected_csvsources_lock.acquire()
    key = (year, month, date, hour, minute, longitude, latitude)
    try:
        if key not in _projected_csvsources:
            _projected_csvsources[key] = _ProjectedCsvSource(year, month, date, hour, minute, longitude, latitude)
    finally:
        _projected_csvsources_lock.release()

    return _projected_csvsources[key]


def main():
    source = CsvSource()
    bounds, stars = source.get_sky_objects(3, 0, 2)
    print bounds
    for star in stars:
        print star


if __name__ == "__main__":
    main()

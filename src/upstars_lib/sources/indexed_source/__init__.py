
import os
import pickle
from datetime import datetime
from time import time
from zipfile import ZipFile
from logging import info

from upstars_lib.coordinates import LonLat, AzAlt, RaDec, get_tile_coords, \
    calculate_bounds, azalt_to_radec, threed_distance
from upstars_lib.projectors import AzAltProjector
from upstars_lib.sky_objects import Star, Line


__all__ = ['IndexedSource']


class IndexedSource(object):
    def __init__(self, year, month, day, hour, minute, longitude, latitude, az_offset=0, dec_offset=0, cache=None):
        self.utc = datetime(year, month, day, hour, minute)
        self.reference_lonlat = LonLat(longitude, latitude)
        self.azalt_offsets = AzAlt(az_offset, dec_offset)

        self.projector = AzAltProjector(self.utc, self.reference_lonlat, self.azalt_offsets)
        self.cache = cache


    def get_coords(self, zoom, x, y):
        bounds = calculate_bounds(zoom, x, y)
        az1, dec1, az2, dec2 = bounds

        mid_az = (az2 - az1) / 2.0 + az1
        mid_dec = (dec1 - dec2) / 2.0 + dec2
        assert get_tile_coords((mid_az, mid_dec), zoom) == (x, y), get_tile_coords((mid_az, mid_dec), zoom)

        radec = self.projector.unproject(AzAlt(mid_az, mid_dec))
        #assert self.projector.project(radec) == AzAlt(mid_az, mid_dec), (self.projector.project(radec), AzAlt(mid_az, mid_dec))

        cx, cy = get_tile_coords(radec, zoom)

        return cx, cy, az1, az2, bounds, radec

    def get_sky_objects(self, zoom, x, y):
        cx, cy, az1, az2, bounds, radec = self.get_coords(zoom, x, y)

        objects = load_tile(zoom, cx, cy, cache=self.cache)
        #objects.append(("#center", radec[0], radec[1], 1))
        projected = perform_star_projections(objects, self.projector, (az1, az2))

        return bounds, projected


    def get_constellation_lines(self, zoom, x, y):
        cx, cy, az1, az2, bounds, radec = self.get_coords(zoom, x, y)
        objects = load_line_tile(zoom, cx, cy, self.cache)
        projected = perform_line_projections(objects, self.projector, (az1, az2))

        return bounds, projected


    def get_labels(self, zoom, x, y):
        cx, cy, az1, az2, bounds, radec = self.get_coords(zoom, x, y)

        objects = load_label_tile(zoom, cx, cy, cache=self.cache)
        projected = perform_label_projections(objects, self.projector, (az1, az2))

        return bounds, projected


    def get_star(self, az, alt):
        radec = self.projector.unproject(AzAlt(az, alt))
        zoom = 6
        cx, cy = get_tile_coords(radec, zoom)
        objects = load_tile(zoom, cx, cy, cache=self.cache)
        nearest = None
        nearest_d = None
        for id, ra, dec, mag in objects:
            object_azalt = self.projector.project(RaDec(ra, dec))
            distance = threed_distance(AzAlt(az, alt), object_azalt)
            if (not nearest) or (nearest_d > distance):
                nearest = (id, object_azalt)
                nearest_d = distance

        return nearest



def load_tile(zoom, x, y, cache=None, prefix="stars-"):
    tile_id = prefix + ("%s-%s-%s" % (zoom, int(x), int(y)))
    tile_filename = "%s-%s-%s.dat" % (zoom, int(x), int(y))
    tile_zip = prefix + ("%s.zip" % zoom)

    start = time()
    if cache:
        result = cache.get(tile_id)
        if result:
            info("Using cached tile %s retrieved %.1fs" % (tile_id, time()-start))
            return result

    if zoom in range(0, 11):
        datafile = os.path.join(os.path.dirname(__file__), tile_zip)
        zf = ZipFile(datafile, "r")
        try:
            f = zf.open(tile_filename)
            try:
                result = pickle.load(f)
            finally:
                f.close()
        finally:
            zf.close()

        if cache:
            cache.set(tile_id, result)

        info("Loaded tile %s retrieved %.1fs" % (tile_id, time()-start))

        return result
    else:
        raise Exception("Invalid zoom", zoom)


def load_line_tile(zoom, x, y, cache=None):
    return load_tile(zoom, x, y, cache=cache, prefix="lines-")


def load_label_tile(zoom, x, y, cache=None):
    return load_tile(zoom, x, y, cache=cache, prefix="labels-")


def project_point(projector, az1, az2, radec):
    p, r = projector.project(radec)
    if (abs(p - az1) > abs(p - az1 + 24) or
        abs(p - az2) > abs(p - az2 + 24)):
        p = p + 24
    elif (abs(p - az1) > abs(p - az1 - 24) or abs(p - az2) > abs(p - az2 - 24)):
        p = p - 24
    return p, r


def perform_star_projections(sky_objects, projector, az_bounds):
    start = time()
    projected = []
    az1, az2 = az_bounds

    for sky_object in sky_objects:
        id, ra, dec, mag = sky_object

        p, r = project_point(projector, az1, az2, (ra, dec))
        projected.append(Star(id, None, AzAlt(p, r), mag))

    info("Completed %d projections after %.1f seconds" % (len(projected), time() - start))
    return projected


def perform_label_projections(sky_objects, projector, az_bounds):
    start = time()
    projected = []
    az1, az2 = az_bounds

    for sky_object in sky_objects:
        id, ra, dec, name = sky_object

        p, r = project_point(projector, az1, az2, (ra, dec))
        projected.append(Star(id, name, AzAlt(p, r), None))

    info("Completed %d projections after %.1f seconds" % (len(projected), time() - start))
    return projected


def perform_line_projections(sky_objects, projector, az_bounds):
    start = time()
    projected = []
    az1, az2 = az_bounds

    for sky_object in sky_objects:
        radec1, radec2 = sky_object
        azalt1 = project_point(projector, az1, az2, radec1)
        azalt2 = project_point(projector, az1, az2, radec2)
        projected.append(Line(AzAlt(*azalt1), AzAlt(*azalt2)))

    info("completed %d projections after %.1f seconds" % (len(projected), time() - start))
    return projected

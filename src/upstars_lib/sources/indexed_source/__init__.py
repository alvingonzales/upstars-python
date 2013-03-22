
import os
import pickle
from datetime import datetime
from time import time
from zipfile import ZipFile

from upstars_lib.coordinates import LonLat, AzAlt, get_tile_coords, \
    calculate_bounds, azalt_to_radec
from upstars_lib.projectors import AzAltProjector
from upstars_lib.sky_objects import Star, Line


__all__ = ['IndexedSource']


class IndexedSource(object):
    def __init__(self, year, month, day, hour, minute, longitude, latitude, az_offset=0, dec_offset=0):
        self.utc = datetime(year, month, day, hour, minute)
        self.reference_lonlat = LonLat(longitude, latitude)
        self.azalt_offsets = AzAlt(az_offset, dec_offset)

        self.projector = AzAltProjector(self.utc, self.reference_lonlat, self.azalt_offsets)
        #self.cache_namespace = "tiles-%s/%s/%s/%s/%s/%s/%s/%s/%s" % (year, month, day, hour, minute, longitude, latitude, az_offset, dec_offset)
        #self.cache = cache

    def get_sky_objects(self, zoom, x, y):
        bounds = calculate_bounds(zoom, x, y)
        az1, dec1, az2, dec2 = bounds
        mid_az = (az2 - az1)/2.0 + az1
        mid_dec = (dec1 - dec2)/2.0 + dec2
        assert get_tile_coords((mid_az, mid_dec), zoom) == (x, y), get_tile_coords((mid_az, mid_dec), zoom)

        radec = azalt_to_radec(self.utc, AzAlt(mid_az, mid_dec), self.reference_lonlat)
        cx, cy = get_tile_coords(radec, zoom)

        objects = load_tile(zoom, cx, cy)
        projected = perform_projections(objects, self.projector, (az1, az2))

        return bounds, projected


def load_tile(zoom, x, y):
    if zoom in range(5, 11):
        datafile = os.path.join(os.path.dirname(__file__), "%s.zip" % zoom)
        zf = ZipFile(datafile, "r")
        try:
            f = zf.open("%s-%s-%s.dat" % (zoom, int(x), int(y)))
            try:
                result = pickle.load(f)
            finally:
                f.close()
        finally:
            zf.close()

        return result
    else:
        raise Exception("Invalid zoom", zoom)


def perform_projections(sky_objects, projector, az_bounds):
    start = time()
    projected = []
    az1, az2 = az_bounds
    for sky_object in sky_objects:
        if isinstance(sky_object, Star):
            (p, r) = projector.project(sky_object.radec)

            if (abs(p-az1) > abs(p-az1+24)
                or abs(p-az2) > abs(p-az2+24)):
                p = p + 24
            elif (abs(p-az1) > abs(p-az1-24)
                  or abs(p-az2) > abs(p-az2-24)):
                p = p - 24

            projected.append(Star(sky_object.id, sky_object.name, AzAlt(p, r), sky_object.mag))
            #projected.append((p, r, sky_object.mag, sky_object))
#            assert p >= 0 and p <= 24
#            if p <= 3 or p >= 21:
#                if r >= -30 and r <= 30:
#                    projected.append((p, r, sky_object.mag, sky_object.id))
        else:
            raise Exception("do not know how to handle %s" % sky_object)

    print "completed %d projections after %.1f seconds" % (len(projected), time() - start)

    return projected


def compose_tiles(projected_sky_objects):
    start = time()
    tiles = {}
    for (p, r, mag, id) in projected_sky_objects:
        for zoom in range(3, 10):
            if mag < 4 + zoom:
                x, y = get_tile_coords((p, r), zoom)
                key = "%d-%d-%d" % (zoom, x, y)

                if key not in tiles:
                    tiles[key] = []

                tiles[key].append((p, r, mag, id))

    print "completed tiling %d after %.1f seconds" % (len(tiles), time() - start)

    averages = {}
    for k in tiles:
        z = k.split("-")[0]
        if z not in averages:
            averages[z] = (0, 0)

        sum, count = averages[z]
        sum = sum + len(tiles[k])
        count = count + 1
        averages[z] = (sum, count)

    stats = {}
    stats["total tiles"] = len(tiles)
    for z in sorted(averages.keys()):
        stats["zoom %d" % zoom] = "%d tiles %.1f avg objects/tile" % (count, sum/float(count))


    return stats, tiles



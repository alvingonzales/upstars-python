
import pickle
import gzip
import os
from time import time
from datetime import datetime
from upstars_lib.projectors import AzAltProjector
from upstars_lib.coordinates import LonLat, AzAlt, get_tile_coords, calculate_bounds
from upstars_lib.sky_objects import Star, Line

__all__ = ['OnDemandSource']

_SKY_OBJECTS_FILE = os.path.join(os.path.dirname(__file__), "objects.dat.gz")
_SKY_OBJECTS = None

class OnDemandSource(object):
    def __init__(self, year, month, day, hour, minute, longitude, latitude, az_offset=0, dec_offset=0, cache=None):
        utc = datetime(year, month, day, hour, minute)
        reference_lonlat = LonLat(longitude, latitude)
        azalt_offsets = AzAlt(az_offset, dec_offset)

        self.projector = AzAltProjector(utc, reference_lonlat, azalt_offsets)
        self.cache_namespace = "tiles-%s/%s/%s/%s/%s/%s/%s/%s/%s" % (year, month, day, hour, minute, longitude, latitude, az_offset, dec_offset)
        self.cache = cache


    def pre_cache(self):
        sky_objects = get_all_sky_objects()
        projections = perform_projections(sky_objects, self.projector)
        stats, tiles = compose_tiles(projections)
        two_hours = 60*60*2

        unset_tiles = self.cache.set_multi(tiles, time=two_hours, namespace=self.cache_namespace)

        meta = {
            'stats': stats,
            'tiles': set(tiles.keys()),
            'unset-tiles': unset_tiles,
        }

        self.cache.set_multi(meta, time=two_hours, namespace=self.cache_namespace)

        if unset_tiles:
            # do something here
            pass

        return meta


    def get_sky_objects(self, zoom, x, y):
        bounds = calculate_bounds(zoom, x, y)
        key = "%d-%d-%d" % (zoom, x, y)
        data = self.cache.get_multi(['tiles', key], namespace=self.cache_namespace)

        if key in data:
            result = (Star(star, star, AzAlt(az, alt), mag) for (az, alt, mag, star) in data[key])
        else:
            result = ()

        return bounds, result


def get_all_sky_objects():
    global _SKY_OBJECTS
    if not _SKY_OBJECTS:
        print "Warning, loading %s into memory, request may be slow" % _SKY_OBJECTS_FILE
        start = time()
        f = gzip.open(_SKY_OBJECTS_FILE, "rb")
        try:
            _SKY_OBJECTS = pickle.load(f)
        finally:
            f.close()

        print "Complete loading %s after %.1fs" % (_SKY_OBJECTS_FILE, time() - start)
    return _SKY_OBJECTS


def perform_projections(sky_objects, projector):
    start = time()
    projected = []
    for object_id in sky_objects:
        sky_object = sky_objects[object_id]
        if isinstance(sky_object, Star):
            (p, r) = projector.project(sky_object.radec)
            assert p >= 0 and p <= 24
            if p <= 3 or p >= 21:
                if r >= -30 and r <= 30:
                    projected.append((p, r, sky_object.mag, sky_object.id))
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



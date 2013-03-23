import os
import pickle
import multiprocessing

from upstars_lib.coordinates import get_tile_coords
from utils.rotation import azalt_to_vector
from math import sqrt

_SKY_OBJECTS = None

def get_all_sky_objects():
    global _SKY_OBJECTS

    from upstars_lib.sources.ondemand_source import get_all_sky_objects as _get_all_sky_objects
    if not _SKY_OBJECTS:
        _SKY_OBJECTS = _get_all_sky_objects()

    return _SKY_OBJECTS


def vector3_distance(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2

    d2 = (x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2
    d = sqrt(d2)
    return d



def build_tile(params):
    hparts, vparts, zoom, x, y = params

    hparts_size = 24.0 / hparts
    vparts_size = 180.0 / vparts

    v1 = azalt_to_vector(0, 0)
    v2 = azalt_to_vector(hparts_size, vparts_size)

    min_distance = vector3_distance(v1, v2)
    hour = ((x * hparts_size + hparts_size / 2.0) + 12) % 24
    deg = 90 - y * vparts_size - vparts_size / 2.0
    mid_v = azalt_to_vector(hour, deg)

    tile_coords = get_tile_coords((hour, deg), zoom)
    assert tile_coords == (x, y + vparts / 2), (tile_coords, (x, y + vparts / 2))

    tile_id = "%s-%s-%s" % (zoom, x, y + vparts / 2)
    tile_objects = []

    print "Building", tile_id

    for sky_object in get_all_sky_objects().values():
        object_v = azalt_to_vector(*sky_object.radec)
        if vector3_distance(mid_v, object_v) <= min_distance:
            obj = (sky_object.id, sky_object.name, sky_object.radec.ra, sky_object.radec.dec, sky_object.mag)

            if sky_object.name:
                tile_objects.append(obj)
            continue

            if zoom >= 9:
                tile_objects.append(obj)

            if sky_object.mag <= 6 + (zoom - 5)*2:
                tile_objects.append(obj)

            continue

    tile_objects.sort(key=lambda o:o.mag, reverse=True)

    print "Tile: %s Objects: %d" % (tile_id, len(tile_objects))

    zpath = os.path.join("../indexes", str(zoom))
    try:
        os.mkdir(zpath)
    except:
        pass

    f = open(os.path.join(zpath, "%s.dat"%tile_id), "wb")
    try:
        pickle.dump(tile_objects, f)
    finally:
        f.close()


def build_index(zoom):
    hparts = 2**zoom
    vparts = hparts / 2

    for x in range(hparts):
        for y in range(vparts):

            #build_tile(hparts, vparts, zoom, x, y)

            yield hparts, vparts, zoom, x, y


def build_indexes():
    if not os.path.exists("../indexes"):
        os.mkdir("../indexes")

    for zoom in range(5, 10):
        for hparts, vparts, zoom, x, y in build_index(zoom):
            yield hparts, vparts, zoom, x, y


def main():
    pool = multiprocessing.Pool(4)
    #build_tile(hparts, vparts, zoom, x, y)
    pool.map(build_tile, build_indexes())


if __name__ == "__main__":
    main()



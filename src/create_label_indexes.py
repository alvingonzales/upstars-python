import os
import pickle
import multiprocessing
from math import sqrt

from upstars_lib.coordinates import get_tile_coords
from utils.rotation import azalt_to_vector
from utils.hyg_database import get_stars


INDEX_DIR="../label-indexes"

EXEMPTIONS = {
    33607: 0, # SAO6022 Camelopardalis
    29924: 0, # SAO13788 Camelopardalis
}


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

    min_distance = vector3_distance(v1, v2)*1.5
    hour = ((x * hparts_size + hparts_size / 2.0) + 12) % 24
    deg = 90 - y * vparts_size - vparts_size / 2.0
    mid_v = azalt_to_vector(hour, deg)

    tile_coords = get_tile_coords((hour, deg), zoom)
    assert tile_coords == (x, y + vparts / 2), (tile_coords, (x, y + vparts / 2))

    tile_id = "%s-%s-%s" % (zoom, x, y + vparts / 2)
    tile_objects = []

    for star in get_stars():
        object_v = azalt_to_vector(star.ra, star.dec)
        if vector3_distance(mid_v, object_v) <= min_distance:
            if zoom >= 6:
                star_name = star.proper_name or star.bayer_flamsteed
            else:
                star_name = star.proper_name

            if not star_name:
                continue

            obj = (star.id, star.ra, star.dec, star_name)

#            # Some stars that are part of our constellations do not have
#            # B/F designation. Need to make sure they're shown at all zoom levels
#            if star.id in EXEMPTIONS and zoom >= EXEMPTIONS[star.id]:
#                tile_objects.append(obj)
#                continue
#
#            # Always show stars if they have a proper name or part of a constellation
#            # excluding Gliese designation
#            if star.bayer_flamsteed or star.proper_name:
#                tile_objects.append(obj)
#                continue

            # All stars visible by zoom 7
            if zoom >= 7:
                tile_objects.append(obj)
                continue

            if star.mag <= 6 + (zoom - 5):
                tile_objects.append(obj)

    tile_objects.sort(key=lambda o: o[3], reverse=True)

    print "Tile: %s Objects: %d" % (tile_id, len(tile_objects))

    zpath = os.path.join(INDEX_DIR, str(zoom))
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


def build_indexes(zoom_range):
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)

    for zoom in zoom_range:
        for hparts, vparts, zoom, x, y in build_index(zoom):
            yield hparts, vparts, zoom, x, y

def main():
    pool = multiprocessing.Pool(2)
    #build_tile(hparts, vparts, zoom, x, y)
    pool.map(build_tile, build_indexes(range(5, 6)))
    #map(build_tile, build_indexes([5]))


    print "Complete!"
    raw_input()


if __name__ == "__main__":
    main()



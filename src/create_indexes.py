import os
import pickle
import multiprocessing
import shutil
import zipfile
from math import sqrt

from upstars_lib.coordinates import get_tile_coords
from utils.rotation import azalt_to_vector
from utils.hyg_database import get_stars


TEMP_INDEX_DIR = "../indexes"
INDEX_DIR = "upstars_lib/sources/indexed_source"
ZIP_PREFIX = "stars-"


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

    min_distance = vector3_distance(v1, v2)
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
            obj = (star.id, star.ra, star.dec, star.mag)

            # Some stars that are part of our constellations do not have
            # B/F designation. Need to make sure they're shown at all zoom levels
            if star.id in EXEMPTIONS and zoom >= EXEMPTIONS[star.id]:
                tile_objects.append(obj)
                continue

            # Always show stars if they have a proper name or part of a constellation
            # excluding Gliese designation
            if star.bayer_flamsteed or star.proper_name:
                tile_objects.append(obj)
                continue

            # All stars visible by zoom 7
            if zoom >= 7:
                tile_objects.append(obj)
                continue

            if star.mag <= 6 + (zoom - 5):
                tile_objects.append(obj)

    tile_objects.sort(key=lambda o: o[3], reverse=True)

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
            yield hparts, vparts, zoom, x, y


def build_indexes(zoom):
    pool = multiprocessing.Pool(2)
    pool.map(build_tile, build_index(zoom))


def zipify(zoom, zoom_dir):
    zip_path = os.path.join(INDEX_DIR, "%s%s.zip" % (ZIP_PREFIX, zoom))
    zf = zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED)
    try:
        for index_file in os.listdir(zoom_dir):
            index_path = os.path.join(zoom_dir, index_file)
            zf.write(index_path, index_file)
    finally:
        zf.close()



def main():
    if not os.path.exists(TEMP_INDEX_DIR):
        os.mkdir(TEMP_INDEX_DIR)

    for zoom in range(6, 7):
        zoom_dir = os.path.join(TEMP_INDEX_DIR, str(zoom))
        if os.path.exists(zoom_dir):
            shutil.rmtree(zoom_dir)

        build_indexes(6)

        zipify(zoom, zoom_dir)

    print "Complete!"
    raw_input()


if __name__ == "__main__":
    main()



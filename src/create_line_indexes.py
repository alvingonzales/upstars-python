import os
import pickle
import multiprocessing
import csv
from upstars_lib.coordinates import get_tile_coords
from utils.rotation import azalt_to_vector
from math import sqrt

_LINES = None


def get_all_lines():
    global _LINES

    if not _LINES:
        csv_path = "../support/ConstellationLinesAll2002.csv"
        f = open(csv_path, "r")
        lines = []
        try:
            constellations_csv = csv.reader(f)
            for _ in range(8):
                constellations_csv.next()

            previous_coords = None
            for row in constellations_csv:
                star_name = row[1]
                coords_ra = row[2]
                coords_dec = row[3]

                current_coords = None
                if star_name:
                    current_coords = float(coords_ra), float(coords_dec)

                if previous_coords and current_coords:
                    lines.append((previous_coords, current_coords))

                previous_coords = current_coords

        finally:
            f.close()

        _LINES = lines

    return _LINES


def vector3_distance(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2

    d2 = (x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2
    d = sqrt(d2)
    return d


# http://geomalgorithms.com/a02-_lines.html
def point_to_segment_distance(p, segment):
    p0, p1 = segment
    v = p1 - p0
    w = p - p0

    c1 = w.dot(v)
    if c1 <= 0:
        return vector3_distance(p, p0)

    c2 = v.dot(v)
    if c2 <= c1:
        return vector3_distance(p, p1)

    b = float(c1)/float(c2)
    pb = p0 + b*v

    return vector3_distance(p, pb)


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

    for radec1, radec2 in get_all_lines():
        p0 = azalt_to_vector(*radec1)
        p1 = azalt_to_vector(*radec2)
        segment = (p0, p1)

        if point_to_segment_distance(mid_v, segment) <= min_distance:
            tile_objects.append((radec1, radec2))

    print "Tile: %s Objects: %d" % (tile_id, len(tile_objects))

    zpath = os.path.join("../line-indexes", str(zoom))
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


def build_indexes(r):
    if not os.path.exists("../line-indexes"):
        os.mkdir("../line-indexes")

    for zoom in r:
        for hparts, vparts, zoom, x, y in build_index(zoom):
            yield hparts, vparts, zoom, x, y

from utils.vectors import V as vector

def main():
    pool = multiprocessing.Pool(4)
#    #build_tile(hparts, vparts, zoom, x, y)
    pool.map(build_tile, build_indexes(range(3, 5)))



if __name__ == "__main__":
    main()



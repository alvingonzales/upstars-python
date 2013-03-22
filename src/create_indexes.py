import os
import pickle

from upstars_lib.coordinates import get_tile_coords
from upstars_lib.sources.ondemand_source import get_all_sky_objects
from utils.rotation import azalt_to_vector
from math import sqrt

SKY_OBJECTS = get_all_sky_objects()

def vector3_distance(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2

    d2 = (x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2
    d = sqrt(d2)
    return d


def build_index(zoom):
    hparts = 2**zoom
    vparts = hparts / 2

    hparts_size = 24.0 / hparts
    vparts_size = 180.0 / vparts

    v1 = azalt_to_vector(0, 0)
    v2 = azalt_to_vector(hparts_size, vparts_size)
    min_distance =  vector3_distance(v1, v2)


    for x in range(hparts):
        for y in range(vparts):
            hour = ((x*hparts_size + hparts_size/2.0) + 12) % 24
            deg = 90 - y*vparts_size - vparts_size/2.0
            mid_v = azalt_to_vector(hour, deg)

            tile_coords = get_tile_coords((hour, deg), zoom)
            assert  tile_coords == (x, y + vparts/2), (tile_coords, (x, y + vparts/2))
            tile_id = "%s-%s-%s" % (zoom, x, y+vparts/2)
            tile_objects = []


            for sky_object in SKY_OBJECTS.values():
                object_v = azalt_to_vector(*sky_object.radec)
                if vector3_distance(mid_v, object_v) <= min_distance:
                    if sky_object.name:
                        tile_objects.append(sky_object)
                        continue

                    if zoom >=9:
                        tile_objects.append(sky_object)

                    if sky_object.mag <= 6 + (zoom - 5):
                        tile_objects.append(sky_object)
                        continue

            tile_objects.sort(key=lambda o: o.mag, reverse=True)

            yield tile_id, tile_objects


def build_indexes():
    if not os.path.exists("indexes"):
        os.mkdir("indexes")

    for zoom in range(5, 11):
        zpath = os.path.join("indexes", str(zoom))
        if not os.path.exists(zpath):
            os.mkdir(zpath)

        for tile_id, tile_objects in build_index(zoom):
            print "Tile: %s Objects: %d" % (tile_id, len(tile_objects))

            f = open(os.path.join(zpath, "%s.dat"%tile_id), "wb")
            try:
                pickle.dump(tile_objects, f)
            finally:
                f.close()

if __name__ == "__main__":
    build_indexes()



import os
import csv
import pickle
import gzip
from time import time

from upstars_lib.sky_objects import Star
from upstars_lib.coordinates import RaDec


def hyg_get_sky_objects():
    csv_path = os.path.abspath("../support/hygxyz.csv")

    f = open(csv_path, "r")
    stars = {}
    try:
        constellations_csv = csv.reader(f)
        for i in range(2):
            constellations_csv.next()

        for row in constellations_csv:
            star_id = row[0]
            star_name = row[6] or row[5] or row[4]
            coords_ra = row[7]
            coords_dec = row[8]
            star_magnitude = row[13]

            if star_id not in stars:
                stars[star_id] = Star(star_id, star_name, RaDec(float(coords_ra), float(coords_dec)), float(star_magnitude))
            else:
                raise Exception("Duplicate", star_id)

    finally:
        f.close()

    return stars


def main():
    start = time()

    objects = hyg_get_sky_objects()
    f = gzip.open("upstars_lib/sources/ondemand_source/objects.dat.gz", "wb")
    try:
        pickle.dump(objects, f)
    finally:
        f.close()

    print "completed pickle of view after %.1f seconds" % (time() - start)


if __name__ == "__main__":
    main()



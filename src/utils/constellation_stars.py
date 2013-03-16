import csv
import os

class Star:
    def __init__(self, id, name, ra, dec, mag):
        self.id = id
        self.name = name
        self.ra = ra
        self.dec = dec
        self.mag = mag

    def __str__(self):
        return "<%s.Star(%s, %s, %s, %s, %s)>" % (__name__, self.id, self.name, self.ra, self.dec, self.mag)

def get_sky_objects():
    csv_path = "ConstellationLinesAll2002.csv"
    if __name__ != "__main__":
        csv_path = os.path.join(os.path.dirname(__file__), csv_path)
    f = open(csv_path, "r")
    stars = {}
    try:
        constellations_csv = csv.reader(f)
        for i in range(8):
            constellations_csv.next()

        print repr(constellations_csv)
        for row in constellations_csv:
            constellation_name = row[0]
            star_name = row[1]
            coords_ra = row[2]
            coords_dec = row[3]
            star_magnitude = row[4]

            if star_name:
                star_id = "%s-%s" % (constellation_name, star_name)
                if star_id not in stars:
                    stars[star_id] = Star(constellation_name, star_name, float(coords_ra), float(coords_dec), float(star_magnitude))

    finally:
        f.close()

    return stars.values()

def main():
    for star in get_sky_objects():
        print star

if __name__ == "__main__":
    main()

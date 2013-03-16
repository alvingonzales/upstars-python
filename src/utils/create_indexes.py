import math


#http://www.platoscave.net/blog/2009/oct/5/calculate-distance-latitude-longitude-python/
#def distance(origin, destination):
def distance(ra1, dec1, ra2, dec2):
#    dec1, ra1 = origin
#    dec2, ra2 = destination
    radius = 1 # km

    dlat = math.radians(dec2-dec1)
    dlon = math.radians(ra2-ra1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(dec1)) \
        * math.cos(math.radians(dec2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

print distance(15.0, 0.0, -15.0, 0.0)


def create_star_index(zoom, stars):
    partitions = 2**zoom
    partition_side = 360.0 / partitions

    minimum_distance = distance(0.0, 0.0, 0.0, partition_side) * 1.2

    indexes = {}

    for part_x in range(partitions):
        # part_y ranges 180deg to -180deg
        # We are only interested however for partitions between 90deg to -90deg
        for part_y in range(partitions/4, partitions/2+partitions/4):
            part_middle_ra_deg = part_x * (partition_side / 2)
            part_middle_dec = part_y * (partition_side / 2)
            index_key = "%s,%s,%s" % (zoom, part_x, part_y)
            found_stars = []
            for star in stars:
                # ra raw data is in hours
                star_ra_deg = (star.ra / 24.0) * 360.0
                star_dec = star.dec

                if distance(part_middle_ra_deg, part_middle_dec, star_ra_deg, star_dec) < minimum_distance:
                    found_stars.append(star)

            if found_stars:
                indexes[index_key] = found_stars

    return indexes

def main():
    import constellation_stars
    stars = constellation_stars.get_sky_objects()
    indexes = create_star_index(4, stars)
    for index in indexes.keys():
        print index, len(indexes[index])

if __name__ == "__main__":
    main()





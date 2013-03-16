
def calculate_bounds(zoom, x, y):
        partitions = 2**zoom
        ra_part_size = 24.0 / partitions
        dec_part_size = 360.0 / partitions

        # nw-se: northwest and southeast bounds
        # ra_deg (right ascension) is 0h to 24h
        # dec (declination) is 180deg to -180deg
        nw_ra = x * ra_part_size
        nw_dec = (-y) * dec_part_size + 180.0
        se_ra = nw_ra + ra_part_size
        se_dec = nw_dec - dec_part_size

        return (nw_ra, nw_dec, se_ra, se_dec)


def within_bounds(star, bounds):
    nw_ra, nw_dec, se_ra, se_dec = bounds

    return (nw_ra <= star.ra and nw_dec >= star.dec
        and se_ra > star.ra and se_dec < star.dec)
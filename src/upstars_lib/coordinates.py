
from collections import namedtuple

RaDec = namedtuple("RaDec", "ra dec")
AzAlt = namedtuple("AzAlt", "az, alt")
LonLat = namedtuple("LonLat", "lon, lat")


def calculate_bounds(zoom, x, y):
    partitions = 2**zoom
    ra_part_size = 24.0 / partitions
    dec_part_size = 360.0 / partitions

    # nw-se: northwest and southeast bounds
    # ra_deg (right ascension) is 0h to 24h
    # dec (declination) is 180deg to -180deg
    nw_ra = x * ra_part_size
    # compensate for leaflet
    nw_ra = (nw_ra + 12.0) % 24.0
    nw_dec = (-y) * dec_part_size + 180.0
    se_ra = nw_ra + ra_part_size
    se_dec = nw_dec - dec_part_size

    return (nw_ra, nw_dec, se_ra, se_dec)


def within_bounds(point, bounds):
    ra, dec = point
    nw_ra, nw_dec, se_ra, se_dec = bounds

    return (nw_ra <= ra and nw_dec >= dec
        and se_ra > ra and se_dec < dec)
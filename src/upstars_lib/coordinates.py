from math import sin, asin, cos, acos, pi, floor, tan, sqrt
from collections import namedtuple
from utils.rotation import azalt_to_vector

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


# http://www.convertalot.com/celestial_horizon_co-ordinates_calculator.html
def radec_to_azalt(utc, radec, lonlat):
#    ra, dec = (radec.ra, radec.dec)
    ra, dec = radec
    lon, lat = (lonlat.lon, lonlat.lat)

    ra = ra * 360.0/24.0
    ha = mean_sidereal_time(utc, lon) - ra;
    if (ha < 0):
         ha = ha + 360


#    print "ha:", ha
    # convert degrees to radians
    ha = ha*pi/180
    dec = dec*pi/180
    lat = lat*pi/180

    # compute altitude in radians
    sin_alt = sin(dec)*sin(lat) + cos(dec)*cos(lat)*cos(ha);
    alt = asin(sin_alt)

    # compute azimuth in radians
    # divide by zero error at poles or if alt = 90 deg
    cos_az = (sin(dec) - sin(alt)*sin(lat))/(cos(alt)*cos(lat))
    az = acos(cos_az)

    # convert radians to degrees
    hrz_altitude = alt*180/pi;
    hrz_azimuth = az*180/pi;

    # choose hemisphere
    if (sin(ha) > 0):
        hrz_azimuth = 360 - hrz_azimuth

    hrz_azimuth = hrz_azimuth * 24.0/360.0

    return AzAlt(hrz_azimuth, hrz_altitude)


def azalt_to_radec(utc, azalt, lonlat):
    az, alt = (azalt.az, azalt.alt)
    lon, lat = (lonlat.lon, lonlat.lat)

    az = az * pi/12
    alt = alt * pi/180
    lon = lon * pi/12
    lat = lat * pi/180

    sin_dec = cos(az)*cos(alt)*cos(lat) + sin(alt)*sin(lat)
    dec = asin(sin_dec)

    cos_ha = (sin(alt) - sin(dec)*sin(lat)) / (cos(dec)*cos(lat));
    ha = acos(cos_ha)

    if sin(az) > 0:
        ha = 2*pi - ha

    ha = ha*180/pi
    ra = mean_sidereal_time( utc, lon ) - ha

    dec = round(dec * 180/pi, 9)
    ra = round(ra * 24.0/360.0, 9)

    if ra < 0:
        ra = ra + 24

    assert ra >= 0 and ra <= 24
    assert dec >= -90 and dec <= 90

    return RaDec(ra, dec)


#// Compute the Mean Sidereal Time in units of degrees.
#// Use lon := 0 to get the Greenwich MST.
#// East longitudes are positive; West longitudes are negative
#// returns: time in degrees
def mean_sidereal_time(now, lon):
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second

    if ((month == 1) or (month == 2)):
        year = year - 1
        month = month + 12

    a = floor(year/100.0);
    b = 2 - a + floor(a/4.0);
    c = floor(365.25*year);
    d = floor(30.6001*(month + 1));

    # days since J2000.0
    jd = b + c + d - 730550.5 + day + (hour + minute/60.0 + second/3600.0)/24.0;

    # julian centuries since J2000.0
    jt = jd/36525.0

    # the mean sidereal time in degrees
    mst = 280.46061837 + 360.98564736629*jd + 0.000387933*jt*jt - jt*jt*jt/38710000 + lon;
    mst = mst % 360.0
    return mst


def get_tile_coords(coord, zoom):
    map_tiles = 2**zoom
    h, d = coord

    hours_per_tile = 24.0 / map_tiles
    degrees_per_tile = 360.0 / map_tiles

    # x/hour axis goes left-right from 12 to 24 then 0 to 12
    h = (h + 12) % 24
    hour_tile = floor(h / hours_per_tile)

    # y/deg axis goes top-bottom from +180 to -180
    d = 180 - d
    degree_tile = floor(d / degrees_per_tile)

    assert hour_tile < map_tiles, (zoom, map_tiles, hour_tile)
    assert degree_tile < map_tiles, (zoom, map_tiles, degree_tile)

    return hour_tile, degree_tile


def vector3_distance(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2

    d2 = (x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2
    d = sqrt(d2)
    return d


def threed_distance(azalt1, azalt2):
    v1 = azalt_to_vector(*azalt1)
    v2 = azalt_to_vector(*azalt2)
    return vector3_distance(v1, v2)


def main():
    from datetime import datetime

    for r in range(0, 24*2):
        ra = 0.5*r
        for dec in range(-89, 90):
            lonlat = LonLat(0, 10)
            radec = RaDec(ra, dec)
            utc = datetime.now()

            azalt = radec_to_azalt(utc, radec, lonlat)
            converted_radec = azalt_to_radec(utc, azalt, lonlat)

            assert radec == converted_radec, (radec, azalt, converted_radec)


if __name__ == "__main__":
    main()
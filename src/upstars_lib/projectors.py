
from math import asin, sin, cos, acos, floor, pi
from datetime import datetime

from upstars_lib.coordinates import AzAlt
from utils.rotation import rotate_azalt

class AzAltProjector:
    def __init__(self, date, reference_lonlat, azalt_offsets=None):
        self.date = date
        self.reference_lonlat = reference_lonlat
        self.azalt_offsets = azalt_offsets


    def project(self, object_radec):
        ra_h, dec = object_radec
        ra = ra_h / 24 * 360
        lon, lat = self.reference_lonlat
        az, alt = coord_to_horizon(self.date, ra, dec, lat, lon)
        az = az / 360 * 24

        if self.azalt_offsets:
            daz, dalt = self.azalt_offsets
            az, alt = rotate_azalt(az, alt, daz, dalt)

        return AzAlt(az, alt)


# http://www.convertalot.com/celestial_horizon_co-ordinates_calculator.html
#// compute horizon coordinates from ra, dec, lat, lon, and utc
#// ra, dec, lat, lon in degrees
#// utc is a Date object
#// results returned in hrz_altitude, hrz_azimuth
def coord_to_horizon( utc, ra, dec, lat, lon ):
    ha = mean_sidereal_time( utc, lon ) - ra;
    if (ha < 0):
         ha = ha + 360

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

    print (utc, ra, dec, lat, lon, hrz_azimuth, hrz_altitude)
    return hrz_azimuth, hrz_altitude


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

    print year, month, day, hour, minute, second

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
    print "abcd", a, b, c, d
    print "jd/jt", jd, jt
    print "mst:", mst
    return mst


class TileProjector():
    def __init__(self, tile_size, bounds):
        (azalt1, azalt2) = bounds
        self.left, self.top = azalt1
        self.right, self.bottom = azalt2

        self.pixels_per_az = tile_size / (self.right - self.left)
        self.pixels_per_alt = tile_size / (self.top - self.bottom)


    def project(self, azalt):
        rel_az = azalt.az - self.left
        rel_alt = self.top - azalt.alt

        # fixes for wrap arounds
        if (self.left > azalt.az):
            rel_az2 = azalt.az - self.left + 24
            if abs(rel_az) > abs(rel_az2):
                rel_az = rel_az2

        elif (self.right < azalt.az):
            rel_az2 = azalt.az - self.left - 24
            if abs(rel_az) > abs(rel_az2):
                rel_ra = rel_az2

        box_x = rel_ra * self.pixels_per_az
        box_y = rel_alt * self.pixels_per_alt

        return box_x, box_y


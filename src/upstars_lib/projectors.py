
from math import asin, sin, cos, acos, floor, pi
from datetime import datetime

from upstars_lib.coordinates import AzAlt


class AzAltProjector:
    def __init__(self, date, reference_lonlat):
        self.date = date
        self.reference_lonlat = reference_lonlat
        self.last = _last(date, reference_lonlat.lon)


    def compute_azalt(self, dec, lat, ha):
        # convert to radians
        dec = dec * pi/180
        lat = lat * pi/180
        ha = ha * pi/180

        sin_alt = sin(dec) * sin(lat) + cos(dec) * cos(lat) * cos(ha)
        alt = asin(sin_alt)
        cos_az = (sin(dec) - sin(alt) * sin(lat)) / (cos(alt) * cos(lat))
        az = acos(cos_az)

        if sin(ha) < 0:
            az = 2*pi - az

        # convert result to degrees
        az = az * 180/pi
        alt = alt * 180/pi

        # convert az back to hours for consistency
        az = 24 - (az / 15.0)
        return az, alt


    def project(self, object_radec):
        # http://www2.arnes.si/~gljsentvid10/horizon.html
#        ra, dec = object_radec
        ra_h, dec = object_radec
        ra = ra_h / 24 * 360
        lon, lat = self.reference_lonlat
        ha = self.last - ra

        az, alt = self.compute_azalt(dec, lat, ha)

        return AzAlt(az, alt)


def _last(utc, longitude):
    # http://aa.usno.navy.mil/faq/docs/GAST.php
    y2k_jd = 2451545.0
    jd = _utc_to_jd(utc)
    jd0 = _utc_to_jd(datetime(utc.year, utc.month, utc.day))

    d = jd - y2k_jd
    d0 = jd0 - y2k_jd
    t = d/36525.0

    gmst = 6.697374558 + 0.06570982441908*d0 + 1.00273790935*utc.hour + 0.000026*(t**2)

    om = (125.04 - 0.052954*d) * pi/180
    L = (280.47 +  0.98565*d) * pi/180
    e = (23.4393 - 0.0000004*d) * pi/180
    dw = -0.000319*sin(om) - 0.000024*sin(2*L)

    eqeq = dw*cos(e)

    #raise Exception(om, L, e, dw, eqeq)
    last = gmst + eqeq


    lmst = gmst + longitude
    lmst = lmst % 24
    lmst = lmst/24 * 360
    return lmst


def _utc_to_jd(utc):
    # http://en.wikipedia.org/wiki/Julian_day#Converting_Julian_or_Gregorian_calendar_date_to_Julian_Day_Number
    a = (14 - utc.month) / 12
    y = utc.year + 4800 - a
    m = utc.month + 12*a - 3
    jdn = utc.day + (153*m + 2)/5 + 365*y + y/4 - y/100 + y/400 - 32045
    jd = jdn + (utc.hour - 12)/24.0 + utc.minute/1440.0 + utc.second/86400.0
    return jd


#assert _utc_to_jd(datetime(2000, 1, 1, 12)) ==  2451545.0, '_utc_to_jd'

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



from math import asin, sin, cos, acos, floor
from datetime import datetime

from upstars_lib.coordinates import AzAlt


class AzAltProjector:
    def __init__(self, date, reference_lonlat):
        self.date = date
        self.reference_lonlat = reference_lonlat
        self.lmst = _lmst(date, reference_lonlat.lon)


    def project(self, object_radec):
        # http://www2.arnes.si/~gljsentvid10/horizon.html
        ra_h, dec = object_radec
        ra = ra_h / 24 * 360
        lon, lat = self.reference_lonlat
        ha = self.lmst - ra

        sin_alt = sin(dec)*sin(lat) + cos(dec)*cos(lat)*cos(ha)
        alt = asin(sin_alt)
        cos_az = (sin(dec) - sin(alt)*sin(lat)) / (cos(alt)*cos(lat))
        az_d = acos(cos_az)

        if sin(ha) < 0:
            az_d = 360 - az_d

        # convert back to hours for consistency
        az = az_d / 15.0

        return AzAlt(az, alt)


def _lmst(utc, longitude):
    # http://aa.usno.navy.mil/faq/docs/GAST.php
    y2k = datetime(2000, 1, 1, 12)
    d = (utc - y2k).total_seconds() / 60 / 60 / 24
    gmst = 18.697374558 + 24.06570982441908*d
    lmst = gmst + longitude
    lmst = lmst - floor(lmst / 24)*24
    return lmst


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



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
        az = acos(cos_az)

        if sin(ha) < 0:
            az = 360 - az

        return AzAlt(az, alt)


def _lmst(utc, longitude):
    # http://aa.usno.navy.mil/faq/docs/GAST.php
    y2k = datetime(2000, 1, 1, 12)
    d = (utc - y2k).total_seconds() / 60 / 60 / 24
    gmst = 18.697374558 + 24.06570982441908*d
    lmst = gmst + longitude
    lmst = lmst - floor(lmst / 24)*24
    return lmst



from math import asin, sin, cos, acos, floor, pi
from datetime import datetime

from upstars_lib.coordinates import AzAlt, RaDec, radec_to_azalt, azalt_to_radec
from utils.rotation import rotate_azalt

class AzAltProjector:
    def __init__(self, date, reference_lonlat, azalt_offsets=None):
        self.date = date
        self.reference_lonlat = reference_lonlat
        self.azalt_offsets = azalt_offsets


    def project(self, object_radec):
        az, alt = radec_to_azalt(self.date, object_radec, self.reference_lonlat)

        if self.azalt_offsets:
            daz, dalt = self.azalt_offsets
            az, alt = rotate_azalt(az, alt, daz, dalt)

        return AzAlt(az, alt)


    def unproject(self, azalt):
        if self.azalt_offsets:
            az, alt = azalt
            daz, dalt = self.azalt_offsets
            az, alt = rotate_azalt(az, alt, daz, dalt, True)
            azalt = AzAlt(az, alt)

        ra, dec = azalt_to_radec(self.date, azalt, self.reference_lonlat)

        return RaDec(ra, dec)

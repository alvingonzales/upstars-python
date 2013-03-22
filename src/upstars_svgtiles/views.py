import random
from flask import Blueprint, Response, render_template

try:
    from google.appengine.api.memcache import Client as CacheClient
except ImportError:
    CacheClient = None

#from upstars_lib.sources.ondemand_source import OnDemandSource
from upstars_lib.sources.indexed_source import IndexedSource
from upstars_lib.sky_objects import Line, Star

blueprint = Blueprint("upstars_svgtiles", __name__, template_folder='templates')

#@blueprint.route('/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:longitude>/<int:latitude>/precache')
#def test3(year, month, day, hour, minute, longitude, latitude):
#    source = OnDemandSource(year, month, day, hour, minute, longitude, latitude, 0, 0, CacheClient())
#    meta = source.pre_cache()
#    return str(meta)


@blueprint.route('/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:longitude>/<int:latitude>/<int:zoom>/<int:x>/<int:y>.svg')
def svg2(year, month, day, hour, minute, longitude, latitude, zoom, x, y):
    if CacheClient:
        cache = CacheClient()
    else:
        cache = None

    source = IndexedSource(year, month, day, hour, minute, longitude, latitude, 0, 0, cache)
    return svg_tile(zoom, x, y, source)


def svg_tile(zoom, x, y, source):
    tile_size = 256.0
    bounds, sky_objects = source.get_sky_objects(zoom, x, y)
    nw_ra, nw_dec, _, _ = bounds
    projector = _Projector(tile_size, bounds)
    projected_stars = []
    projected_lines = []
    for sky_object in sky_objects:
        if isinstance(sky_object, Star):
            star = sky_object
            size = (2**(zoom))/(2**star.mag) + .5
            box_x, box_y = projector.project(star.radec)
            projected_stars.append((box_x, box_y, size, star))

        elif isinstance(sky_object, Line):
            line = sky_object
            x1, y1 = projector.project(line.point1)
            x2, y2 = projector.project(line.point2)
            projected_lines.append((x1, y1, x2, y2))
        else:
            raise Exception("cannot handle", sky_object)

    return Response(response=render_template("upstars_svgtiles_tile.svg.txt", z=zoom, ra=nw_ra, dec=nw_dec, x=x, y=y, stars=projected_stars, lines=projected_lines),
                    status=200,
                    mimetype="image/svg+xml")


class _Projector():
    def __init__(self, tile_size, bounds):
        (nw_ra, nw_dec, se_ra, se_dec) = bounds
        self.nw_ra = nw_ra
        self.nw_dec = nw_dec
        self.se_ra = se_ra

        self.pixels_per_ra = tile_size / (se_ra - nw_ra)
        self.pixels_per_dec = tile_size / (nw_dec - se_dec)


    def project(self, point):
        ra, dec = point
        rel_ra = ra - self.nw_ra
        rel_dec = self.nw_dec - dec

        box_x = rel_ra * self.pixels_per_ra
        box_y = rel_dec * self.pixels_per_dec

        return box_x, box_y


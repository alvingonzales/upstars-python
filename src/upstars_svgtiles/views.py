import random
from time import time
from flask import Blueprint, Response, render_template
from logging import info

try:
    from google.appengine.api.memcache import Client as CacheClient
except ImportError:
    CacheClient = None

#from upstars_lib.sources.ondemand_source import OnDemandSource
from upstars_lib.sources.indexed_source import IndexedSource
from upstars_lib.sky_objects import Line, Star

blueprint = Blueprint("upstars_svgtiles", __name__, template_folder='templates', static_folder="static")

@blueprint.route('/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:longitude>/<int:latitude>/<int:azd>/<int:altd>/<int:zoom>/<int:x>/<int:y>.svg')
def svg2(year, month, day, hour, minute, longitude, latitude, azd, altd, zoom, x, y):
    start = time()
    try:
        if CacheClient:
            cache = CacheClient()
        else:
            cache = None

        longitude = longitude / 360.0 * 24.0
        azd = azd / 360.0 * 24.0

        source = IndexedSource(year, month, day, hour, minute, longitude, latitude, azd, altd, cache)

        bounds, sky_objects = source.get_sky_objects(zoom, x, y)
        return svg_tile(zoom, x, y, bounds, sky_objects)
    finally:
        info("Tile generation end %.1fs" % (time() - start))

@blueprint.route('/lines/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:longitude>/<int:latitude>/<int:azd>/<int:altd>/<int:zoom>/<int:x>/<int:y>.svg')
def svg_lines(year, month, day, hour, minute, longitude, latitude, azd, altd, zoom, x, y):
    start = time()
    try:
        if CacheClient:
            cache = CacheClient()
        else:
            cache = None

        longitude = longitude / 360.0 * 24.0
        azd = azd / 360.0 * 24.0

        source = IndexedSource(year, month, day, hour, minute, longitude, latitude, azd, altd, cache)
        bounds, sky_objects = source.get_constellation_lines(zoom, x, y)
        return svg_tile(zoom, x, y, bounds, sky_objects)
    finally:
        info("Tile generation end %.1fs" % (time() - start))


def svg_tile(zoom, x, y, bounds, sky_objects):
    tile_size = 256.0
    nw_ra, nw_dec, _, _ = bounds
    projector = _Projector(tile_size, bounds)
    projected_stars = []
    projected_lines = []
    for sky_object in sky_objects:
        if isinstance(sky_object, Star):
            star = sky_object
            size = (2**(zoom-1))/(2**star.mag) + .5
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


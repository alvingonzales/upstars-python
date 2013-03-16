from flask import Blueprint, Response, render_template
import random

from upstars_lib.sources.csv_source import CsvSource, ProjectedCsvSource
from upstars_lib.sky_objects import Line, Star

blueprint = Blueprint("upstars_svgtiles", __name__, template_folder='templates')

@blueprint.route('/')
def test():
    return "upstars_svgtiles: hello world"


@blueprint.route('/<int:zoom>/<int:x>/<int:y>.svg')
def svg(zoom, x, y):
    source = CsvSource()
    return svg_tile(zoom, x, y, source)


@blueprint.route('/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:longitude>/<int:latitude>/<int:zoom>/<int:x>/<int:y>.svg')
def svg2(year, month, day, hour, minute, longitude, latitude, zoom, x, y):
    source = ProjectedCsvSource(year, month, day, hour, minute, longitude, latitude)
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
            size = (star.mag / 6) * 2 + 1
            box_x, box_y = projector.project(star.radec)
            projected_stars.append((box_x, box_y, size))

        elif isinstance(sky_object, Line):
            line = sky_object
            x1, y1 = projector.project(line.point1)
            x2, y2 = projector.project(line.point2)
            projected_lines.append((x1, y1, x2, y2))

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

        print bounds
        print self.pixels_per_ra
        print self.pixels_per_dec


    def project(self, point):
        ra, dec = point
        rel_ra = ra - self.nw_ra
        rel_dec = self.nw_dec - dec

        # fixes for wrap arounds
        if (self.nw_ra > ra):
            rel_ra2 = ra - self.nw_ra + 24
            if abs(rel_ra) > abs(rel_ra2):
                rel_ra = rel_ra2

        if (self.se_ra < ra):
            rel_ra2 = ra - self.nw_ra - 24
            if abs(rel_ra) > abs(rel_ra2):
                rel_ra = rel_ra2

        box_x = rel_ra * self.pixels_per_ra
        box_y = rel_dec * self.pixels_per_dec




        return box_x, box_y


from flask import Blueprint, Response, render_template
import random
import utils.constellation_stars

blueprint = Blueprint("upstars_svgtiles", __name__, template_folder='templates')
STARS = utils.constellation_stars.get_stars()

@blueprint.route('/')
def test():
    return "upstars_svgtiles: hello world"


def cell_units(zoom):
    cell_ra = 24.0 / 2**zoom
    cell_dec = 180.0 / 2**zoom
    return cell_ra, cell_dec


def topleft(zoom, x, y):
    cell_ra, cell_dec = cell_units(zoom)
    left_ra, top_dec = cell_ra * x, cell_dec * y
    return left_ra, 90 - top_dec


def bounding_box(zoom, x, y):
    left_ra, top_dec = topleft(zoom, x, y)
    right_ra, bottom_dec = topleft(zoom, x+1, y+1)
    return left_ra, top_dec, right_ra, bottom_dec


def find_stars(zoom, x, y):
    left_ra, top_dec, right_ra, bottom_dec = bounding_box(zoom, x, y)
    #found = [star for star in STARS]
    found = [star for star in STARS if (star.ra >= left_ra and star.ra < right_ra and star.dec <= top_dec and star.dec > bottom_dec)]
    return found


def translate(zoom, x, y, box_size, ra, dec):
    cell_ra, cell_dec = cell_units(zoom)
    left_ra, top_dec = topleft(zoom, x, y)
    cell_ra_size = box_size / cell_ra
    cell_dec_size = box_size / cell_dec
    relative_ra = ra - left_ra
    relative_dec = top_dec - dec
    box_x = relative_ra * cell_ra_size
    box_y = relative_dec * cell_dec_size

    return box_x, box_y


@blueprint.route('/<int:zoom>/<int:x>/<int:y>.svg')
def svg(zoom, x, y):
    stars = []
    left_ra, top_dec = topleft(zoom, x, y)

    for star in find_stars(zoom, x, y):
        box_x, box_y = translate(zoom, x, y, 256.0, star.ra, star.dec)
        size = (star.mag / 6) * 2 + 1
        stars.append((box_x, box_y, size))

#    for i in range(100):
#        stars.append((256.0*random.random(), 256.0*random.random(), 2*random.random()))

    return Response(response=render_template("upstars_svgtiles_tile.svg.txt", z=zoom, ra=left_ra, dec=top_dec, x=x, y=y, stars=stars),
                    status=200,
                    mimetype="image/svg+xml")

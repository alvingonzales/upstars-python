from flask import Blueprint, render_template, request
from upstars_lib.sources.indexed_source import IndexedSource
from upstars_lib.caching import CacheClient

blueprint = Blueprint("upstars_web.finder", __name__)

@blueprint.route('')
def find_star():
    year = int(request.args.get("year"))
    month = int(request.args.get("month"))
    day = int(request.args.get("day"))
    hour = int(request.args.get("hour"))
    minute = int(request.args.get("minute"))
    longitude = int(request.args.get("lon"))
    latitude = int(request.args.get("lat"))
    azd = int(request.args.get("az_offset"))
    altd = int(request.args.get("alt_offset"))
    az = float(request.args.get("az"))
    alt = float(request.args.get("alt"))

    longitude = longitude / 360.0 * 24.0
    azd = azd / 360.0 * 24.0

    az = az / 360.0 * 24.0
    if az < 0:
        az = az + 24

    cache = CacheClient()
    source = IndexedSource(year, month, day, hour, minute, longitude, latitude, azd, altd, cache)
    id, azalt = source.get_star(az, alt)

    oaz, oalt = azalt
    assert oaz >= 0
    if oaz > 12:
        oaz = oaz - 24

    return '["%s", "%s", "%s"]' % (id, oaz*360.0/24.0, oalt)

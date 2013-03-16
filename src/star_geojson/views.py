from flask import Blueprint

blueprint = Blueprint("star_geojson", __name__, template_folder='templates')

@blueprint.route('/')
def test():
    return "hello world"
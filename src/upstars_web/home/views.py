from flask import Blueprint, render_template

blueprint = Blueprint("upstars_home", __name__, template_folder='templates', static_folder='static')

@blueprint.route('/')
def index():
    return render_template("index.html")

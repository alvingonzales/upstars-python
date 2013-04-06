from flask import Flask, Response

import upstars_web.home
import upstars_web.svgtiles
import upstars_web.finder

app = Flask(__name__, static_folder='rootstatic')
app.register_blueprint(upstars_web.home.blueprint)
app.register_blueprint(upstars_web.svgtiles.blueprint, url_prefix='/tiles')
app.register_blueprint(upstars_web.finder.blueprint, url_prefix='/find')
if __name__ == "__main__":
    @app.route("/debug/routes")
    def debug_routes():
        links = []
        for rule in app.url_map.iter_rules():
            links.append(repr(rule))

        routes = "\n".join(links)
        return Response(response=routes,
                        status=200,
                        mimetype="text/plain")

    app.run(host="0.0.0.0", debug=True, threaded=False)
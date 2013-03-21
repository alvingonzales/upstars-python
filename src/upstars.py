from flask import Flask, Response

import upstars_home
import upstars_svgtiles

app = Flask(__name__, static_folder='rootstatic')
app.register_blueprint(upstars_home.blueprint)
app.register_blueprint(upstars_svgtiles.blueprint, url_prefix='/tiles')

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

    app.run(host="0.0.0.0", debug=True, threaded=True)
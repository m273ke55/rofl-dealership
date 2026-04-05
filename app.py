from flask import Flask, request

from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.public import public_bp
from routes.requests import requests_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "rofl-dealership-secret"

    @app.before_request
    def method_override_for_ajax():
        override = request.headers.get("X-HTTP-Method-Override", "").upper().strip()
        if override in {"PUT", "DELETE"}:
            request.environ["REQUEST_METHOD"] = override

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(admin_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

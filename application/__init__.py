# coding: utf-8

from flask import Flask

def create_app(config):
    app = Flask(__name__, static_folder='../static')
    app.config.from_pyfile(config)

    from .routes import bpRoutes
    app.register_blueprint(bpRoutes)

    return app

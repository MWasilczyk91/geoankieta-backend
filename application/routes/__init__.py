#coding: utf-8

from flask import Blueprint

bpRoutes = Blueprint('routes', __name__)

from .routes import *

from flask import Blueprint

bp = Blueprint('teams', __name__, url_prefix='/teams')

from .routes import *
from flask import Blueprint

bp = Blueprint('chapters', __name__, url_prefix='/chapters')

from .routes import *
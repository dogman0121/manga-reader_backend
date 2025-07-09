from flask import Blueprint

bp = Blueprint('lists', __name__, url_prefix='/lists')

from .routes import *
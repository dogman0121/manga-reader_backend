from flask import Blueprint

bp = Blueprint('notifications', __name__, url_prefix='/notifications')

from .routes import *
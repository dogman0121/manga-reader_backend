from flask import db, Blueprint

bp = Blueprint('home', __name__, url_prefix='/home')

from .routes import *
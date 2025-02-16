from flask import Blueprint

bp = Blueprint('person', __name__, url_prefix='/person')

import app.user.routes
from flask import Blueprint

bp = Blueprint('search', __name__)

import app.search.routes
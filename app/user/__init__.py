from flask import Blueprint

bp = Blueprint('user', __name__)

import app.person.routes
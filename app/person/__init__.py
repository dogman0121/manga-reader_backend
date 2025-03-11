from flask import Blueprint

bp = Blueprint('person', __name__)

import app.person.routes
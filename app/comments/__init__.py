from flask import Blueprint

bp = Blueprint('comment', __name__)

import app.comments.routes
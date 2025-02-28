from flask import jsonify

from app.search import bp

@bp.route('/', methods=['GET'], slash_redirect=False)
def search():
    return jsonify(
        {
            "id": 1,
            "name": "Борьба в прямом эфире",
            "description": "Это чу чука",
            "year": 2024,
            "views": 100,
            "created_at": "2024-08-14"
        }
    )
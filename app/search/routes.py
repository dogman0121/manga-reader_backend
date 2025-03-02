from flask import jsonify

from app.search import bp

@bp.route('/api/search', methods=['GET'])
def search():
    return jsonify(
        [{
            "id": 1,
            "type": {
                "id": 1,
                "name": "манга"
            },
            "status": {
                "id": 1,
                "name": "выпускается"
            },
            "name": "Борьба в прямом эфире",
            "description": "Это чу чука",
            "poster": "https://cover.imglib.info/uploads/cover/shingeki-no-kyojin/cover/k0HAZuvw2SJw_250x350.jpg",
            "year": 2024,
            "views": 100,
            "created_at": "2024-08-14",
            "updated_at": "2024-08-14",
            "genres": [
                {
                    "id": 1,
                    "name": "Драки"
                },
                {
                    "id": 2,
                    "name": "Седзе"
                },
                {
                    "id": 3,
                    "name": "Романтика"
                }
            ]
        },
        {
            "id": 2,
            "type": {
                "id": 1,
                "name": "манга"
            },
            "status": {
                "id": 1,
                "name": "выпускается"
            },
            "name": "Борьба в прямом эфире",
            "description": "Это чу чука",
            "poster": "https://cover.imglib.info/uploads/cover/shingeki-no-kyojin/cover/k0HAZuvw2SJw_250x350.jpg",
            "year": 2024,
            "views": 100,
            "created_at": "2024-08-14",
            "updated_at": "2024-08-14",
            "genres": [
                {
                    "id": 1,
                    "name": "Драки"
                },
                {
                    "id": 2,
                    "name": "Седзе"
                },
                {
                    "id": 3,
                    "name": "Романтика"
                }
            ]
        },
        ]
    )
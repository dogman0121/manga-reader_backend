from flask import jsonify, request

from app.person.models import Person
from app.search import bp
from app.manga.models import Manga
from app.user.models import User
from app.utils import respond


def parse_manga_filters():
    types = request.args.getlist("type", type=int)
    genres = request.args.getlist("genre", type=int)
    statuses = request.args.getlist("status", type=int)
    adult = request.args.getlist("adult", type=int)


    return {
        "types": types,
        "genres": genres,
        "statuses": statuses,
        "adult": adult
    }

@bp.route('/api/v1/search', methods=['GET'])
def search_v1():
    query = request.args.get('query')
    section = request.args.get('section')

    if section == "manga":
        return respond(data=[ i.to_dict() for i in Manga.get_with_filters(query, **parse_manga_filters()) ])

    if section == "user":
        return respond(data=[i.to_dict() for i in User.search(query)])

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
                    "name": "драки"
                },
                {
                    "id": 2,
                    "name": "дедзе"
                },
                {
                    "id": 3,
                    "name": "домантика"
                }
            ]
        },
        ]
    )
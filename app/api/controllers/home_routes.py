from flask import Blueprint

from app.domain.repositories import manga_repo
from app.schemas.home_schema import HomeSchema
from app.use_cases.home.get_home_blocks import GetHomeBlocks
from app.utils import create_response

bp = Blueprint('home', __name__, url_prefix='/home')

@bp.route('', methods=['GET'], strict_slashes=False)
def get_home():
    schema = HomeSchema()

    res = GetHomeBlocks(manga_repo=manga_repo).execute()

    data = schema.dump(res)

    return create_response(data=data, status_code=200)

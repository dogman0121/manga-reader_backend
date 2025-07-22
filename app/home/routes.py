from . import bp
from .services import HomeService


@bp.route('', methods=['GET'], strict_slashes=False)
def get_home():
    pass

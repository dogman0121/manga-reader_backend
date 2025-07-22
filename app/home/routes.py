from . import bp

@bp.route('', methods=['GET'], strict_slashes=False)
def get_home():
    pass
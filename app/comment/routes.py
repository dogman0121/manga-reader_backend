from flask_jwt_extended import jwt_required

from app.comment import bp
from app.user.models import User
from app.comment.models import Comment

from flask import request, jsonify

from flask_jwt_extended import (jwt_required, get_jwt_identity)

@bp.route('/api/v1/comments', methods=['GET'])
def get_comments_v1():
    manga_id = request.args.get('manga', type=int)
    root_id = request.args.get('root', type=int)
    parent_id = request.args.get('parent', type=int)
    page = request.args.get('page', 1, type=int)


    if manga_id is not None:
        return jsonify([i.to_dict() for i in Comment.get_manga_comments(manga_id=manga_id, page=page)])

    if root_id is not None:
        return jsonify([i.to_dict() for i in Comment.get_comment_descendants(comment_id=root_id, page=page)])

    if parent_id is not None:
        return jsonify([i.to_dict() for i in Comment.get_comment_children(comment_id=parent_id, page=page)])

    return jsonify(msg="Bad request"), 400


@bp.route('/api/v1/comments/<int:comment_id>', methods=['GET'])
def get_comment_v1(comment_id):
    return jsonify(Comment.get(comment_id).to_dict())


@bp.route('/api/v1/comments', methods=['POST'])
@jwt_required()
def add_comment_v1():
    body = request.json

    if body is None:
        return jsonify(msg="Bad Request"), 400

    if not body.get("text"):
        return jsonify(msg="Comment text is empty"), 400

    text = body.get("text")
    user = User.get_by_id(get_jwt_identity())
    root_id = body.get("root")
    parent_id = body.get("parent")
    manga_id = body.get("manga")

    comment = Comment(text=text, creator=user, root_id=root_id, parent_id=parent_id)

    if manga_id:
        comment.add_for_manga(manga_id=manga_id)
    else:
        comment.add()

    return jsonify(comment.to_dict()), 201

@bp.route('/api/v1/comments', methods=['PUT'])
def update_comment_v1():
    pass

@bp.route('/api/v1/comments', methods=['DELETE'])
def delete_comment_v1():
    pass
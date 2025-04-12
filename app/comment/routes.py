from flask_jwt_extended import jwt_required

from app.comment import bp
from app.user.models import User
from app.comment.models import Comment
from app.comment.models import Vote

from flask import request, jsonify

from flask_jwt_extended import (jwt_required, get_jwt_identity)

@bp.route('/api/v1/comments', methods=['GET'])
@jwt_required(optional=True)
def get_comments_v1():
    manga_id = request.args.get('manga', type=int)
    root_id = request.args.get('root', type=int)
    parent_id = request.args.get('parent', type=int)
    page = request.args.get('page', 1, type=int)

    user = User.get_by_id(get_jwt_identity())

    if manga_id is not None:
        return jsonify(data=[i.to_dict(user=user) for i in Comment.get_manga_comments(manga_id=manga_id, page=page)])

    if root_id is not None:
        return jsonify(data=[i.to_dict(user=user) for i in Comment.get_comment_descendants(comment_id=root_id, page=page)])

    if parent_id is not None:
        return jsonify(data=[i.to_dict(user=user) for i in Comment.get_comment_children(comment_id=parent_id, page=page)])

    return jsonify(error={"code": "bad_request"}), 400


@bp.route('/api/v1/comments/<int:comment_id>', methods=['GET'])
@jwt_required(optional=True)
def get_comment_v1(comment_id):
    user = User.get_by_id(get_jwt_identity())

    return jsonify(data=Comment.get(comment_id).to_dict(user=user))


@bp.route('/api/v1/comments', methods=['POST'])
@jwt_required()
def add_comment_v1():
    body = request.json

    if body is None:
        return jsonify(error={"code": "bad_request"}), 400

    if not body.get("text"):
        return jsonify(error={"code": "bad_request"}), 400

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

    return jsonify(data=comment.to_dict()), 201

@bp.route('/api/v1/comments', methods=['PUT'])
def update_comment_v1():
    pass

@bp.route('/api/v1/comments', methods=['DELETE'])
def delete_comment_v1():
    pass

@bp.route('/api/v1/comments/<int:comment_id>/votes', methods=['GET'])
def get_votes_v1(comment_id):
    pass

@bp.route('/api/v1/comments/<int:comment_id>/votes', methods=['POST'])
@jwt_required()
def add_vote_v1(comment_id):
    vote_type = request.json.get("vote")

    if vote_type is None:
        return jsonify(error={"code": "bad_request"}), 400

    comment = Comment.get(comment_id)

    if comment is None:
        return jsonify(error={"code": "not_found"}), 404

    user = User.get_by_id(get_jwt_identity())

    if comment.is_voted_by_user(user):
        vote = comment.get_user_vote(user)
        if vote.type == vote_type:
            vote.delete()
        else:
            vote.type = vote_type
            vote.update()

        return jsonify(data=vote.to_dict()), 200
    else:
        vote = Vote(comment_id=comment_id, type=vote_type, user_id=user.id)
        vote.add()
        return jsonify(data=vote.to_dict()), 200



@bp.route('/api/v1/comments/<int:comment_id>/votes', methods=['DELETE'])
@jwt_required()
def delete_vote_v1(comment_id):
    comment = Comment.get(comment_id)

    if comment is None:
        return jsonify(error={"code": "not_found"}), 404

    comment.delete()

    return jsonify(data=None), 204
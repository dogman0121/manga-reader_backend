from flask_jwt_extended import jwt_required

from app.comments import bp
from app.user.models import User
from app.comments.models import Comment
from app.comments.models import Vote

from app.utils import respond

from flask import request

from flask_jwt_extended import (jwt_required, get_jwt_identity)

@bp.route('/api/v1/comments', methods=['GET'])
@jwt_required(optional=True)
def get_comments_v1():
    manga_id = request.args.get('manga', type=int)
    chapter_id = request.args.get('chapter', type=int)
    root_id = request.args.get('root', type=int)
    parent_id = request.args.get('parent', type=int)
    page = request.args.get('page', 1, type=int)

    user = User.get_by_id(get_jwt_identity())

    if manga_id is not None:
        return respond(data=[i.to_dict(user=user) for i in Comment.get_manga_comments(manga_id=manga_id, page=page)])

    if chapter_id is not None:
        return respond(data=[i.to_dict(user=user) for i in Comment.get_chapter_comments(chapter_id=chapter_id, page=page)])

    if root_id is not None:
        return respond(data=[i.to_dict(user=user) for i in Comment.get_comment_descendants(comment_id=root_id, page=page)])

    if parent_id is not None:
        return respond(data=[i.to_dict(user=user) for i in Comment.get_comment_children(comment_id=parent_id, page=page)])

    return respond(error="bad_request"), 400


@bp.route('/api/v1/comments/<int:comment_id>', methods=['GET'])
@jwt_required(optional=True)
def get_comment_v1(comment_id):
    user = User.get_by_id(get_jwt_identity())

    return respond(data=Comment.get(comment_id).to_dict(user=user))


@bp.route('/api/v1/comments', methods=['POST'])
@jwt_required()
def add_comment_v1():
    json = request.json

    if json is None:
        return respond(error="bad_request"), 400

    if not json.get("text"):
        return respond(error="bad_request"), 400

    text = json.get("text")
    user = User.get_by_id(get_jwt_identity())
    root_id = json.get("root")
    parent_id = json.get("parent")
    chapter_id = json.get("chapter")
    manga_id = json.get("manga")

    comment = Comment(text=text, creator=user, root_id=root_id, parent_id=parent_id)

    if manga_id:
        comment.entity_type = "manga"
        comment.entity_id = manga_id
    elif chapter_id:
        comment.entity_type = "chapter"
        comment.entity_id = chapter_id

    comment.add()

    return respond(data=comment.to_dict()), 201

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
        return respond(error="bad_request"), 400

    comment = Comment.get(comment_id)

    if comment is None:
        return respond(error="not_found"), 404

    user = User.get_by_id(get_jwt_identity())

    if comment.is_voted_by_user(user):
        vote = comment.get_user_vote(user)
        if vote.type == vote_type:
            vote.delete()
        else:
            vote.type = vote_type
            vote.update()

        return respond(data=vote.to_dict()), 200
    else:
        vote = Vote(comment_id=comment_id, type=vote_type, user_id=user.id)
        vote.add()
        return respond(data=vote.to_dict()), 200



@bp.route('/api/v1/comments/<int:comment_id>/votes', methods=['DELETE'])
@jwt_required()
def delete_vote_v1(comment_id):
    comment = Comment.get(comment_id)

    if comment is None:
        return respond(error="not_found"), 404

    comment.delete()

    return respond(data=None), 204
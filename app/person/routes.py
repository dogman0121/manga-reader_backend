from flask import jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)
from app.person import bp
from app.person.models import Person


@bp.route('/api/person/create', methods=['POST'])
@jwt_required()
def add_person():
    name = request.json['name']

    if Person.get_by_name(name):
        return jsonify(msg=f"Person already exists")

    person = Person(name=name, creator_id=get_jwt_identity())
    person.add()

    return jsonify(person.to_dict())

@bp.route('/api/person/<int:person_id>', methods=['GET'])
def get_person(person_id):
    person = Person.get(person_id)

    if person is None:
        return jsonify(msg='Person not found'), 404

    return jsonify(person.to_dict())

@bp.route('/api/person/<int:person_id>', methods=['PUT'])
@jwt_required()
def update_person():
    pass

@bp.route('/api/person/<int:person_id>/subscribe', methods=['GET'])
@jwt_required()
def subscribe_person(person_id):
    pass

@bp.route('/api/person/<int:person_id>/unsubscribe', methods=['GET'])
@jwt_required()
def unsubscribe_person(person_id):
    pass



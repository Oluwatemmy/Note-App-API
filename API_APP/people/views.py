from flask import request
from flask_restx import Resource, Namespace, fields
from ..utils import db
from http import HTTPStatus
from ..models.views import Note, Person

people_namespace = Namespace('People', description='People operations')

people_field = people_namespace.model(
    'People Model', {
        'name': fields.String(required=True, description='Name of the person'),
        'email': fields.String(required=True, description='Email of the person')
    }
)

return_field = people_namespace.model(
    'People List Model', {
        'id': fields.Integer(),
        'name': fields.String(description='Name of the Person'),
        'email': fields.String(description='Email of the person')
    }
)


@people_namespace.route('')
class PeopleList(Resource):
    @people_namespace.doc('Return all users')
    @people_namespace.marshal_with(return_field)
    def get(self):
        """
            Return all users
        """
        return Person.query.all(), HTTPStatus.OK

    @people_namespace.doc('Create a user')
    @people_namespace.expect(people_field)
    def post(self):
        """
            Create a new user and prevents blank creation of a user
        """
        data = request.get_json()

        # check if user already exists
        if Person.query.filter_by(email=data.get('email')).first():
            return {
                'message': 'User already exists'
            }, HTTPStatus.BAD_REQUEST
        
        name = data.get('name')
        email = data.get('email')

        # Add User to Database
        if name and email:
            new_person = Person(name=name, email=email)
            try:
                new_person.save()
                return {
                    'message': 'User {} created successfully'.format(new_person.name)
                }, HTTPStatus.CREATED
            except Exception as e:
                db.session.rollback()
                return {
                    'message': 'Something went wrong'
                }, HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            return {'message': 'Please fill all fields'}, HTTPStatus.BAD_REQUEST

@people_namespace.route('/<int:person_id>')
class People(Resource):
    @people_namespace.doc('Return a user')
    @people_namespace.marshal_with(return_field)
    def get(self, person_id):
        """
            Return a specific user
        """
        person = Person.query.filter_by(id=person_id).first()
        if person:
            return person, HTTPStatus.OK
        else:
            return {
                'message': 'User not found'
            }, HTTPStatus.NOT_FOUND

    @people_namespace.doc('Update a user')
    @people_namespace.expect(people_field)
    def put(self, person_id):
        """
            Update a user by ID
        """
        person = Person.query.filter_by(id=person_id).first()
        if person:
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            if name and email:
                # check if user email exists before
                if Person.query.filter_by(email=email).first():
                    return {
                        'message': 'User already exists'
                    }, HTTPStatus.BAD_REQUEST
                person.name = name
                person.email = email
                try:
                    person.save()
                    return {
                        'message': 'User {} updated successfully'.format(person.name)
                    }, HTTPStatus.OK
                except Exception as e:
                    db.session.rollback()
                    return {
                        'message': 'Something went wrong'
                    }, HTTPStatus.INTERNAL_SERVER_ERROR
            else:
                return {'message': 'Please fill all fields'}, HTTPStatus.BAD_REQUEST
        else:
            return {
                'message': 'User not found'
            }, HTTPStatus.NOT_FOUND

    @people_namespace.doc('Delete a user')
    @people_namespace.response(HTTPStatus.NO_CONTENT, 'User deleted')
    def delete(self, person_id):
        """
            Delete a user by ID
        """
        person = Person.query.filter_by(id=person_id).first()
        if person:
            person.delete()
            return {
                'message': 'User deleted successfully'
            }, 200
        else:
            return {
                'message': 'User not found'
            }, HTTPStatus.NOT_FOUND
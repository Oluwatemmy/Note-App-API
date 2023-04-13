from datetime import datetime
from flask import request
from flask_restx import Resource, Namespace, fields
from ..utils import db
from ..models.views import Note, Person
from http import HTTPStatus

note_namespace = Namespace('Note', description='Note operations')

note_field = note_namespace.model(
    'Note Model', {
        'content': fields.String(required=True, description='Content of the note'),
        'author_id': fields.Integer(required=True, description='Person id of the note')
    }
)

return_field = note_namespace.model(
    'Note List Model', {
        'author_id': fields.Integer(description='Person id of the note'),
        'content': fields.String(description='Content of the note'),
        'created_at': fields.DateTime(description='Created at of the note')
    }
)

update_field = note_namespace.model(
    'Note Update Model', {
        'content': fields.String(description='Content of the note')
    }
)


@note_namespace.route('')
class NoteList(Resource):
    @note_namespace.doc('Return all notes')
    @note_namespace.marshal_with(return_field)
    def get(self):
        """
            Return all notes
        """
        return Note.query.all(), HTTPStatus.OK

    @note_namespace.doc('Create a note')
    @note_namespace.expect(note_field)
    def post(self):
        """
            Create a note
        """
        data = request.get_json()
        author_id = data.get("author_id")
        content = data.get("content")

        # check for blank input
        if not author_id or not content:
            return {
                'message': 'Missing author_id or content'
            }, HTTPStatus.BAD_REQUEST
        
        # check if author exists
        if not Person.get_by_id(author_id):
            return {
                'message': 'Author does not exist'
            }, HTTPStatus.BAD_REQUEST
        
        new_note = Note(
            content=content,
            author_id=author_id
        )
        
        try:
            new_note.save()
            return {
                'message': 'Note created successfully'
            }, HTTPStatus.CREATED
        except Exception as e:
            db.session.rollback()
            return {
                'message': 'An error occurred while creating the note'
            }, HTTPStatus.INTERNAL_SERVER_ERROR


@note_namespace.route('/<int:note_id>')
class Notes(Resource):
    @note_namespace.doc('Return a note')
    @note_namespace.marshal_with(return_field)
    def get(self, note_id):
        """
            Return a note by ID
        """
        # check if note exists
        note = Note.query.filter_by(id=note_id).first()
        if not note:
            return {
                'message': 'Note does not exist'
            }, HTTPStatus.NOT_FOUND
        
        return note, HTTPStatus.OK


    @note_namespace.doc('Update a note')
    @note_namespace.expect(update_field)
    @note_namespace.marshal_with(return_field)
    def put(self, note_id):
        """
            Update a note by ID
        """
        data = request.get_json()
        content = data.get("content")

        # check for blank input
        if not content:
            return {
                'message': 'Missing author_id or content'
            }, HTTPStatus.BAD_REQUEST
        
        note = Note.query.filter_by(id=note_id).first()
        # Check if note exists
        if note:
            note.content = content
            note.save()
            return note, 200
        else:
            return {
                "message": "Note not Found"
            }, HTTPStatus.NOT_FOUND

    @note_namespace.doc('Delete a note')
    def delete(self, note_id):
        """
            Delete a Note by ID
        """
        note = Note.query.filter_by(id=note_id).first()
        # Check if note exists
        if note:
            note.delete()
            return {
                "message": "Note deleted Successfully"
            }, 200
        else:
            return {
                "message": "Note not Found"
            }, HTTPStatus.NOT_FOUND
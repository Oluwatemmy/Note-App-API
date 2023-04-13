from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate
from .utils import db
from .notes.views import note_namespace
from .people.views import people_namespace

def create_app():
    app = Flask(__name__)

    SECRET_KEY = "26de89f59d0c9f12eb1e7806cd7236"
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    migrate = Migrate(app, db)

    api = Api(
        app, 
        version='1.0.0', 
        title='Notes APP API', 
        description='A Note app where users can create, read, update and delete their notes.'
    )

    api.add_namespace(note_namespace, path='/note')
    api.add_namespace(people_namespace, path='/people')

    @app.before_first_request
    def create_tables():
        db.create_all()

    return app

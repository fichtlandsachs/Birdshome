from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pwd import getpwnam
from grp import getgrnam
import os


db = SQLAlchemy()


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)

    user_uuid = getpwnam('pi')[2]
    grp_uuid = getgrnam('users')[2]

    path_media = os.path.join(os.path.dirname(__file__), 'static', 'media')
    path_outputs = os.path.join(os.path.dirname(__file__), 'outputs')
    path_video = os.path.join(os.path.dirname(__file__), 'static', 'media', 'videos')
    path_photo = os.path.join(os.path.dirname(__file__), 'static', 'media', 'photos')
    path_charts = os.path.join(os.path.dirname(__file__), 'static', 'media', 'charts')

    if not os.path.exists(path_media):
        os.makedirs(path_media)
        os.chown(path_media, user_uuid, grp_uuid)

    if not os.path.exists(path_video):
        os.makedirs(path_video)
        os.chown(path_video, user_uuid, grp_uuid)

    if not os.path.exists(path_photo):
        os.makedirs(path_photo)
        os.chown(path_photo, user_uuid, grp_uuid)
    if not os.path.exists(path_charts):
        os.makedirs(path_charts)
        os.chown(path_charts, user_uuid, grp_uuid)

    if not os.path.exists(path_outputs):
        os.makedirs(path_outputs)
        os.chown(path_outputs, user_uuid, grp_uuid)

    if app.config['ENV'] == 'development':
        app.config.from_object('config.DevConfig')
    elif app.config['ENV'] == 'production':
        app.config.from_object('config.ProdConfig')
    else:
        app.config.from_object('config.Config')
    db.init_app(app)
    app.app_context().push()
    with app.app_context():
        from . import models
        from . import routes
        # Create tables for our models
        db.create_all()
        return app

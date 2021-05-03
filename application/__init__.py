import os
from grp import getgrnam
from pwd import getpwnam

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from application import constants
from config import Config as cfg

db = SQLAlchemy()
appConfigKeys = [
    [constants.PICTURE, constants.ENDING_PIC],
    [constants.PICTURE, constants.PREFIX_PIC],
    [constants.PICTURE, constants.LATEST_PIC_RES_X],
    [constants.PICTURE, constants.LATEST_PIC_RES_Y],

    [constants.DATA, constants.ACTIVITY_LIST_OUT],
    [constants.DATA, constants.ACTIVITY_LIST_END],

    [constants.VIDEO, constants.DURATION_VID],
    [constants.VIDEO, constants.PREFIX_VID],
    [constants.VIDEO, constants.VID_RES_X],
    [constants.VIDEO, constants.VID_RES_Y],
    [constants.VIDEO, constants.VID_FRAMES],
    [constants.VIDEO, constants.VID_LABEL_FORMAT],
    [constants.VIDEO, constants.VID_FOURCC],
    [constants.VIDEO, constants.VID_FORMAT],
    [constants.VIDEO, constants.SOUND_FORMAT],

    [constants.REPLAY, constants.PREFIX_VID_REPLAY],
    [constants.REPLAY, constants.FRAMES_PER_SEC_REPLAY],
    [constants.REPLAY, constants.PREFIX_VID_REPLAY],
    [constants.REPLAY, constants.REPLAY_INTERVAL],
    [constants.REPLAY, constants.REPLAY_DAYS],
    [constants.REPLAY, constants.REPLAY_ENABLED],

    [constants.SMB, constants.SERVER_UPLOAD_ENABLED],
    [constants.SMB, constants.TIME_UPLOAD],
    [constants.SMB, constants.FOLDER_UPLOAD],
    [constants.SMB, constants.SERVER_UPLOAD],
    [constants.SMB, constants.PAUSE_RETRY_UPLOAD],
    [constants.SMB, constants.NUM_RETRY_UPLOAD],

    [constants.SYSTEM, constants.TIME_FORMAT_FILE],
    [constants.SYSTEM, constants.SENSITIVITY],
    [constants.SYSTEM, constants.WIREDATEI_TEMP_NEST],
    [constants.SYSTEM, constants.WIREDATEI_TEMP_OUT],
    [constants.SYSTEM, constants.OUTPUT_FOLDER],
    [constants.SYSTEM, constants.UPLOAD_FOLDER_REPLAY],
    [constants.SYSTEM, constants.UPLOAD_FOLDER_PIC],
    [constants.SYSTEM, constants.UPLOAD_FOLDER_CHART],
    [constants.SYSTEM, constants.UPLOAD_FOLDER_VID],
    [constants.SYSTEM, constants.UPLOAD_FOLDER_VID_NO],
    [constants.SYSTEM, constants.UPLOAD_FOLDER_PERSONAS],

    [constants.NEST_CONFIG, constants.FIRST_VISIT],
    [constants.NEST_CONFIG, constants.DATE_EGG],
    [constants.NEST_CONFIG, constants.DATE_CHICK],
    [constants.NEST_CONFIG, constants.DATE_LEAVE],
    [constants.NEST_CONFIG, constants.NAME_BIRD]
]


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('app.cfg', silent=True)
    user_uuid = getpwnam('pi')[2]
    grp_uuid = getgrnam('users')[2]

    path_media = os.path.join(app.root_path, cfg.OUTPUT_FOLDER, cfg.MEDIA_FOLDER)
    path_outputs = os.path.join(app.root_path, cfg.FOLDER_CSV_FILE_OUTPUT)
    path_video = os.path.join(app.root_path, cfg.OUTPUT_FOLDER, cfg.UPLOAD_FOLDER_VID)
    path_photo = os.path.join(app.root_path, cfg.OUTPUT_FOLDER, cfg.UPLOAD_FOLDER_PIC)
    path_charts = os.path.join(app.root_path, cfg.OUTPUT_FOLDER, cfg.UPLOAD_FOLDER_CHART)
    path_replay = os.path.join(app.root_path, cfg.OUTPUT_FOLDER, cfg.UPLOAD_FOLDER_REPLAY)
    path_general = os.path.join(app.root_path, cfg.OUTPUT_FOLDER, cfg.UPLOAD_FOLDER_PERSONAS)

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

    if not os.path.exists(path_replay):
        os.makedirs(path_replay)
        os.chown(path_replay, user_uuid, grp_uuid)

    if not os.path.exists(path_general):
        os.makedirs(path_general)
        os.chown(path_general, user_uuid, grp_uuid)

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
        engine = db.get_engine(app=app)
        db.metadata.create_all(bind=engine, checkfirst=True)
        app = updateConfiguration(app)
        return app


def updateConfiguration(_app):
    validateInitialSetup(_app)
    from application.handler.database_hndl import DBHandler
    _db = DBHandler(_app.config[constants.SQLALCHEMY_DATABASE_URI])
    for entry in appConfigKeys:
        _app.config[entry[1]] = _db.getConfigEntry(entry[0], entry[1])
    return _app


def validateInitialSetup(_app):
    from application.handler.database_hndl import DBHandler
    _db = DBHandler(_app.config[constants.SQLALCHEMY_DATABASE_URI])
    for entry in appConfigKeys:

        if not _db.checkConfigEntryExists(entry[0], entry[1]):
            _db.createUpdateConfigEntry(entry[0], entry[1], _app.config[entry[1]])
    _db.createUpdateConfigEntry(constants.SYSTEM, constants.ROOT_PATH_APPLICATION, _app.root_path)


def updateSetup(_app):
    from application.handler.database_hndl import DBHandler
    _db = DBHandler(_app.config[constants.SQLALCHEMY_DATABASE_URI])
    for entry in appConfigKeys:
        _db.createUpdateConfigEntry(entry[0], entry[1], _app.config[entry[1]])

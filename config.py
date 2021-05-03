import os
import socket


class Config:
    """Base config vars."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = '8EEz4lmKbvhnZF3j2M1CkxWK97IX1Hh1'
    """"Default configuration Server Upload"""
    SERVER_UPLOAD_ENABLED = False
    PAUSE_RETRY_UPLOAD = 5
    NUM_RETRY_UPLOAD = 3
    FOLDER_UPLOAD = ''
    SERVER_UPLOAD = ''
    TIME_UPLOAD = '21:00'
    """"Default configuration Video"""
    DURATION_VID = 15
    PREFIX_VID = socket.gethostname() + '_'
    VID_RES_X = 1280
    VID_RES_Y = 720
    VID_FRAMES = 30
    VID_FOURCC = 'avc1'
    VID_FORMAT = '.mp4'
    SOUND_FORMAT = '.wav'
    VID_ENDINGS = ['*.mp4', '*.avi']
    VID_LABEL_FORMAT = '%d.%m.%Y %H:%M:%S'

    """Default replay Configuration"""
    REPLAY_ENABLED = False
    FRAMES_PER_SEC_REPLAY = 30
    REPLAY_INTERVAL = 10
    REPLAY_DAYS = 7
    PREFIX_VID_REPLAY = socket.gethostname() + '_'

    """Default picture Configuration"""
    PREFIX_PIC = socket.gethostname() + '_'
    ENDING_PIC = '.jpg'
    LATEST_PIC_RES_X = '1280'
    LATEST_PIC_RES_Y = '720'

    """Default activity download Configuration"""
    ACTIVITY_LIST_OUT = 'BirdsActivity'
    ACTIVITY_LIST_END = '.xlsx'

    NAME_BIRD = ''
    DATE_CHICK = None
    DATE_EGG = None
    FIRST_VISIT = None
    DATE_LEAVE = None

    SENSITIVITY = 3000

    REPLAY_ENABLED = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////etc/birdshome/database/birdshome_base.db'
    # Bezeichnung der Temperaturfühler im Verzeichnis /sys/bus/w1/devices
    WIREDATEI_TEMP_NEST = '28-02148107cbff'
    WIREDATEI_TEMP_OUT = '28-0317252964ff'
    # Start measurement at 4lx resolution. Time typically 16ms.
    CONTINUOUS_LOW_RES_MODE = 0x13
    # Start measurement at 1lx resolution. Time typically 120ms
    CONTINUOUS_HIGH_RES_MODE_1 = 0x10
    # Start measurement at 0.5lx resolution. Time typically 120ms
    CONTINUOUS_HIGH_RES_MODE_2 = 0x11
    # Start measurement at 1lx resolution. Time typically 120ms
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_HIGH_RES_MODE_1 = 0x20
    # Start measurement at 0.5lx resolution. Time typically 120ms
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_HIGH_RES_MODE_2 = 0x21
    # Start measurement at 1lx resolution. Time typically 120ms
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_LOW_RES_MODE = 0x23
    DEVICE_DENSITY = 0x23
    OUTPUT_FOLDER = os.path.join('static')
    MEDIA_FOLDER = 'media'
    FOLDER_CSV_FILE_OUTPUT = 'outputs'
    UPLOAD_FOLDER_REPLAY = os.path.join('media', 'replay')
    UPLOAD_FOLDER_PIC = os.path.join('media', 'photos')
    UPLOAD_FOLDER_CHART = os.path.join('media', 'charts')
    UPLOAD_FOLDER_VID = os.path.join('media', 'videos')
    UPLOAD_FOLDER_VID_NO = os.path.join('media', 'videos', 'no_detect')
    UPLOAD_FOLDER_PERSONAS = os.path.join('media', 'general')

    TIME_FORMAT_FILE = "%d%m%Y%H%M%S"
    TEMPLATES_AUTO_RELOAD = True


class ProdConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////etc/birdshome/database/birdshome.db'


class DevConfig(Config):
    DEBUG = True
    TESTING = True
    FLASK_DEBUG = 1
    SQLALCHEMY_DATABASE_URI = 'sqlite:////etc/birdshome/database/birdshome_dev.db'

import os
import socket


class Config:
    """Base config vars."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////etc/birdshome/birdshome_base.db'
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
    OUTPUT_FOLDER = os.path.join('application', 'static')
    UPLOAD_FOLDER_PIC = os.path.join('media', 'photos')
    UPLOAD_FOLDER_CHART = os.path.join('media', 'charts')
    UPLOAD_FOLDER_VID = os.path.join('media', 'videos')
    UPLOAD_FOLDER_VID_NO = os.path.join('media', 'videos', 'no_detect')
    PIC_ENDING = '.jpg'
    VID_ENDINGS = ['*.m4p', '*.avi']
    ACTIVITY_LIST_OUT = 'BirdsActivity'
    ACTIVITY_LIST_END = '.xlsx'
    LATEST_PIC = socket.gethostname() + '_'
    LATEST_VID = socket.gethostname() + '_'
    LATEST_PIC_RES_X = '640'
    LATEST_PIC_RES_Y = '480'
    VID_RES_X = 1280
    VID_RES_Y = 720
    VID_FRAMES = 30
    TIME_FORMATE = "%d%m%Y%H%M%S"
    TEMPLATES_AUTO_RELOAD = True


class ProdConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////etc/birdshome/birdshome.db'


class DevConfig(Config):
    DEBUG = True
    TESTING = True
    FLASK_DEBUG = 1
    SQLALCHEMY_DATABASE_URI = 'sqlite:////etc/birdshome/birdshome_dev.db'

import datetime
import os
import pathlib
import threading
import time
from time import sleep

import cv2

from application import constants
from application.handler.database_hndl import DBHandler


class ScreenShotHandler:

    def __init__(self, app):
        self.app = app
        self.vc = self.app.config[constants.VIDEO_CAPTURE_INST]
        self.db = DBHandler(self.app.config[constants.SQLALCHEMY_DATABASE_URI])
        self.nextScreenShot = datetime.datetime.now() + datetime.timedelta(
            minutes=int(self.app.config[constants.REPLAY_INTERVAL]))

    def take_picture(self):
        while True:
            enabled = self.db.getConfigEntry(constants.REPLAY, constants.REPLAY_ENABLED)
            timer = int(float(self.db.getConfigEntry(constants.REPLAY, constants.REPLAY_INTERVAL))) * 60
            if enabled:
                check, frame = self.vc.read()
                if check:
                    # Converting color image to gray_scale image
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    self.createScreenShot(gray)
                    sleep(timer)
                    enabled = self.db.getConfigEntry(constants.REPLAY, constants.REPLAY_ENABLED)
            else:
                sleep(180)

    def createScreenShot(self, frame):

        fileName_short = self.app.config[constants.PREFIX_PIC] + datetime.datetime.now().strftime(
            self.app.config[constants.TIME_FORMAT_FILE]) + str(self.app.config[constants.ENDING_PIC])
        full_filename = os.path.join(os.path.dirname(self.app.root_path),
                                     str(self.app.config[constants.OUTPUT_FOLDER]),
                                     str(self.app.config[constants.UPLOAD_FOLDER_REPLAY]),
                                     fileName_short)
        cv2.imwrite(full_filename, frame)

    def startTread(self):
        "Launches the screen recording function using a thread"
        screenShot_thread = threading.Thread(target=self.take_picture())
        screenShot_thread.start()

    def createReplay(self):
        enabled = self.db.getConfigEntry(constants.REPLAY, constants.REPLAY_ENABLED)

        if enabled:
            if not self.db.checkConfigEntryExists(constants.REPLAY, constants.REPLAY_LAST_STARTTIME):
                self.db.createUpdateConfigEntry(constants.REPLAY, constants.REPLAY_LAST_STARTTIME,
                                                datetime.datetime.strftime(
                                                    self.db.getConfigEntry(constants.SYSTEM,
                                                                           constants.TIME_FORMAT_FILE)))

            startTime = datetime.timedelta(days=self.db.getConfigEntry(constants.REPLAY, constants.REPLAY_DAYS))
            framesPerSec = self.db.getConfigEntry(constants.REPLAY, constants.FRAMES_PER_SEC_REPLAY)
            replayFormat = self.db.getConfigEntry(constants.VIDEO, constants.VID_FORMAT)
            codec = self.db.getConfigEntry(constants.VIDEO, constants.VID_FOURCC)
            videoRatio = (self.db.getConfigEntry(constants.VIDEO, constants.VID_RES_X),
                          self.db.getConfigEntry(constants.VIDEO, 'VID_RES_Y'))
            fourcc = cv2.cv2.VideoWriter_fourcc(args=codec)

            pic_path = os.path.join(self.db.getConfigEntry(constants.SYSTEM, constants.ROOT_PATH_APPLICATION),
                                    self.db.getConfigEntry(constants.SYSTEM, constants.OUTPUT_FOLDER),
                                    self.db.getConfigEntry(constants.SYSTEM, constants.UPLOAD_FOLDER_REPLAY))
            picturesList = list(sorted(
                pathlib.Path(pic_path).glob('*' + str(self.db.getConfigEntry(constants.PICTURE, constants.ENDING_PIC)),
                                            key=os.path.getmtime)))

            outputFile = pic_path + '/replay_' + datetime.datetime.strftime(
                self.db.getConfigEntry(constants.SYSTEM, constants.TIME_FORMAT_FILE)) + replayFormat

            vr = cv2.cv2.VideoWriter(outputFile, fourcc, int(framesPerSec), videoRatio)

            for pic in picturesList:
                time_createion = time.ctime(os.path.getctime(pic))
                if time_createion > startTime:
                    ret, frame = cv2.cv2.VideoCapture(pic)
                    if ret:
                        vr.write(frame)
            vr.release()

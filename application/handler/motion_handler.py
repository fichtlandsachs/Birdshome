import datetime
import os
from time import sleep

import cv2

from application import constants
from application.handler.audio_handler import AudioRecorder
from application.handler.database_hndl import DBHandler
from application.handler.video_audio_merger import AudioVideoMerge
from application.handler.video_handler import VideoRecorder


class Motion_Handler:

    def __init__(self, app=None):
        self.app = app
        self.vc = app.config[constants.VIDEO_CAPTURE_INST]
        self.video_height = self.app.config[constants.LATEST_PIC_RES_X]
        self.video_width = self.app.config[constants.LATEST_PIC_RES_Y]
        self.prefix = self.app.config[constants.PREFIX_PIC]
        self.db = DBHandler(app.config[constants.SQLALCHEMY_DATABASE_URI])
        self.folderName = os.path.join(app.root_path, app.config[constants.OUTPUT_FOLDER],
                                       app.config[constants.UPLOAD_FOLDER_VID])
        self.nextScreenShot = datetime.datetime.now() + datetime.timedelta(
            minutes=int(app.config[constants.REPLAY_INTERVAL]))

    def detect(self):
        # Assigning our static_back to None
        static_back = None
        count = 0
        # Initializing DataFrame, one column is start
        # time and other column is end time
        nextReadTime = datetime.datetime.now() + datetime.timedelta(minutes=10)
        sensitivity = None
        while True:

            if datetime.datetime.now() > nextReadTime or sensitivity is None:
                sensitivity = int(self.app.config[constants.SENSITIVITY])
                nextReadTime = datetime.datetime.now() + datetime.timedelta(minutes=10)
            # Reading frame(image) from video
            check, frame = self.vc.read()

            # Initializing motion = 0(no motion)
            motion = 0

            # Converting color image to gray_scale image
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Converting gray scale image to GaussianBlur
            # so that change can be find easily
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # In first iteration we assign the value
            # of static_back to our first frame
            if static_back is None:
                static_back = gray
                continue
            if count == 100:
                static_back = gray
                count = 0
            # Difference between static background
            # and current frame(which is GaussianBlur)
            diff_frame = cv2.absdiff(static_back, gray)

            # If change in between static background and
            # current frame is greater than 30 it will show white color(255)
            thresh_frame = cv2.threshold(diff_frame, 50, 255, cv2.THRESH_BINARY)[1]
            thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

            # Finding contour of moving object
            _, cnts, _ = cv2.findContours(thresh_frame.copy(),
                                          cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in cnts:
                if cv2.contourArea(contour) < sensitivity:
                    continue
                motion = 1
                # (x, y, w, h) = cv2.boundingRect(contour)
                # Hier wäre der Punkt wenn eingegrenzt werden muss hinsichtlich des Bereiches
                # in dem die Bewegung erkannt wurde
                self.db.create_birdMove('cam1')

                self.startRecording()
                sleep(5)
                # Appending status of motion
            sleep(.33)
            count = count + 1

    def startRecording(self):
        timeFormat = self.app.config[constants.TIME_FORMAT_FILE]
        timestamp_file = datetime.datetime.now().strftime(timeFormat)
        fileVideo_short = self.prefix + timestamp_file + self.app.config[constants.VID_FORMAT]
        fileAudio_short = self.prefix + timestamp_file + self.app.config[constants.SOUND_FORMAT]
        full_FileName = self.prefix + '_' + timestamp_file + self.app.config[constants.VID_FORMAT]
        full_VideoFile = os.path.join(self.folderName, fileVideo_short)
        full_AudioFile = os.path.join(self.folderName, fileAudio_short)
        full_finalFile = os.path.join(self.folderName, full_FileName)
        self.record(full_finalFile, full_VideoFile, full_AudioFile)

    def record(self, full_filename, video_fileName, audio_fileName):

        delta = int(self.app.config[constants.DURATION_VID])
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        vHandler = VideoRecorder(video_fileName, endTime, self.app.config[constants.SQLALCHEMY_DATABASE_URI], self.vc)
        aHandler = AudioRecorder(audio_fileName, endTime)

        vHandler.start()
        aHandler.start()
        sleep(35)
        vHandler.stop()
        aHandler.stop()
        mHandler = AudioVideoMerge(full_filename, video_fileName, audio_fileName)
        mHandler.start()

    def stop(self):
        pass


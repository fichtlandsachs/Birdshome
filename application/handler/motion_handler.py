import datetime
import os
from time import sleep

import cv2
import pandas

from application.handler.audio_handler import AudioRecorder
from application.handler.video_audio_merger import AudioVideoMerge
from application.handler.video_handler import VideoRecorder


class Motion_Handler():

    def __init__(self, vc, vidHeigth, vidWidth, fileNamePrefix, folder):
        self.vc = vc
        self.video_height = vidHeigth
        self.video_width = vidWidth
        self.prefix = fileNamePrefix
        self.folderName = folder

    def detect(self):
        # Assigning our static_back to None
        static_back = None
        # List when any moving object appear
        motion_list = [None, None]
        count = 0
        # Time of movement
        time = []
        # Initializing DataFrame, one column is start
        # time and other column is end time
        df = pandas.DataFrame(columns=["Start", "End"])
        while True:
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
                if cv2.contourArea(contour) < 3000:
                    continue
                motion = 1
                # (x, y, w, h) = cv2.boundingRect(contour)
                # Hier wäre der Punkt wenn eingegrenzt werden muss hinsichtlich des Bereiches
                # in dem die Bewegung erkannt wurde
                self.startRecording()
                sleep(5)
                # Appending status of motion
            sleep(.33)
            count = count + 1

    def startRecording(self):
        timestamp_file = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
        fileVideo_short = self.prefix + timestamp_file + '.avi'
        fileAudio_short = self.prefix + timestamp_file + '.wav'
        full_FileName = self.prefix + '_' + timestamp_file + '.avi'
        full_VideoFile = os.path.join(self.folderName, fileVideo_short)
        full_AudioFile = os.path.join(self.folderName, fileAudio_short)
        full_finalFile = os.path.join(self.folderName, full_FileName)
        self.record(full_finalFile, full_VideoFile, full_AudioFile)

    def record(self, full_filename, video_fileName, audio_fileName):
        delta = 15  # time for taking a video
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        vHandler = VideoRecorder(self.vc, video_fileName, endTime, delta, self.video_height, self.video_width)
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

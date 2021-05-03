import datetime
import threading

import cv2
import numpy as np

from application import constants
from application.handler.database_hndl import DBHandler


def _draw_label(img, text, pos):
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = .4
    color = (255, 255, 255)

    cv2.putText(img, text, pos, font_face, scale, color, 1, cv2.LINE_AA)


class VideoRecorder:

    def __init__(self, fileName, recordingTime, dbURL, vc):

        self.open = True
        self.dbURL = dbURL
        self.video_cap = vc
        self.fileName = fileName
        self.vidFrames = []
        self.frame = []
        self.vid_Out = None
        self.endTime = recordingTime

    def record(self):
        vidframe = []
        db = DBHandler(self.dbURL)
        vid_duration = int(db.getConfigEntry(constants.VIDEO, constants.DURATION_VID))
        label_format = str(db.getConfigEntry(constants.VIDEO, constants.VID_LABEL_FORMAT))
        fourcc = str(db.getConfigEntry(constants.VIDEO, constants.VID_FOURCC))
        vid_Height = int(db.getConfigEntry(constants.VIDEO, constants.VID_RES_Y))
        vid_Width = int(db.getConfigEntry(constants.VIDEO, constants.VID_RES_X))
        while self.endTime > datetime.datetime.now():
            ret, frame = self.video_cap.read()
            np_image = np.array(frame)
            if ret:
                _draw_label(frame, datetime.datetime.now().strftime(label_format), (20, 20))

                vidframe = [[np_image], [datetime.datetime.now().strftime(label_format)]]
                self.vidFrames.append(vidframe)
                cv2.waitKey(33)
            else:
                break
        vidframe.clear()
        i = len(self.vidFrames)
        video_frames_num = i / vid_duration
        fourcc = cv2.cv2.VideoWriter_fourcc(fourcc[0], fourcc[1], fourcc[2], fourcc[3])
        self.vid_Out = cv2.cv2.VideoWriter(self.fileName, fourcc, video_frames_num,
                                           (vid_Height, vid_Width),
                                           False)
        while i > 1:
            curr_viFrame = self.vidFrames.pop(0)
            frame = curr_viFrame[0][0]
            gray = cv2.cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2GRAY)
            time_val = datetime.datetime.strptime(curr_viFrame[1].pop(), label_format)
            _draw_label(gray, time_val.strftime(label_format), (20, 20))
            self.vid_Out.write(gray)
            i = len(self.vidFrames)
        self.vid_Out.release()

    def start(self):
        "Launches the video recording function using a thread"
        video_thread = threading.Thread(target=self.record)
        video_thread.start()

    def stop(self):
        "Finishes the video recording therefore the thread too"
        if self.open:
            self.open = False
            self.vidFrames.clear()

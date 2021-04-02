import datetime
import threading

import cv2
import numpy as np


class VideoRecorder:

    def __init__(self, video_cap, fileName, recordingTime, delta, vid_height, vid_width):
        self.open = True
        self.vid_duration = delta
        self.video_cap = video_cap
        self.fileName = fileName
        self.vidFrames = []
        self.frame = []
        self.vid_Height = vid_height
        self.vid_Width = vid_width
        self.vid_Out = None
        self.endTime = recordingTime

    def record(self):

        while self.endTime > datetime.datetime.now():
            ret, frame = self.video_cap.read()
            np_image = np.array(frame)
            if ret:
                self._draw_label(frame, datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), (20, 20))

                vidframe = [[np_image], [datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")]]
                self.vidFrames.append(vidframe)
                cv2.waitKey(33)
            else:
                break
        vidframe.clear()
        i = len(self.vidFrames)
        video_frames_num = i / self.vid_duration
        fourcc = cv2.cv2.VideoWriter_fourcc(*'XVID')
        self.vid_Out = cv2.cv2.VideoWriter(self.fileName, fourcc, video_frames_num, (self.vid_Height, self.vid_Width),
                                           False)
        while i > 1:
            curr_viFrame = self.vidFrames.pop(0)
            frame = curr_viFrame[0][0]
            gray = cv2.cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2GRAY)
            time_val = datetime.datetime.strptime(curr_viFrame[1].pop(), "%d.%m.%Y %H:%M:%S")
            self._draw_label(gray, time_val.strftime("%d.%m.%Y %H:%M:%S"), (20, 20))
            self.vid_Out.write(gray)
            i = len(self.vidFrames)

    def start(self):
        "Launches the video recording function using a thread"
        video_thread = threading.Thread(target=self.record)
        video_thread.start()

    def stop(self):
        "Finishes the video recording therefore the thread too"
        if self.open:
            self.open = False
            self.vidFrames.clear()

    def _draw_label(self, img, text, pos):
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        scale = .4
        color = (255, 255, 255)

        cv2.putText(img, text, pos, font_face, scale, color, 1, cv2.LINE_AA)

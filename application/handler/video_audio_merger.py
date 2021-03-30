import os
import subprocess
import threading
from time import sleep


class AudioVideoMerge:

    def __init__(self, fileName, videoFile, audioFile):
        self.fileName = fileName
        self.videoFile = videoFile
        self.audioFile = audioFile

    def start(self):
        video_thread = threading.Thread(target=self.merge())
        video_thread.start()

    def merge(self):
        cmd = "ffmpeg -y -i " + self.videoFile + " -i " + self.audioFile + " -vcodec copy -acodec copy " \
               + self.fileName
        subprocess.call(cmd, shell=True)
        #sleep(5)
        os.remove(self.videoFile)
        os.remove(self.audioFile)

    def stop(self):
        pass

import datetime
import threading
import wave

import pyaudio


class AudioRecorder:
    "Audio class based on pyAudio and Wave"

    def __init__(self, filename, recordingTime, rate=44100, fpb=4096, channels=1):
        self.open = True
        self.rate = rate
        self.frames_per_buffer = fpb
        self.channels = channels
        self.format = pyaudio.paInt16
        self.audio_filename = filename
        self.audio = pyaudio.PyAudio()
        self.recordTime = recordingTime
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.frames_per_buffer)
        self.audio_frames = []

    def record(self):
        "Audio starts being recorded"
        self.stream.start_stream()
        while datetime.datetime.now() < self.recordTime:
            data = self.stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)
            if not self.open:
                break

    def start(self):
        "Launches the video recording function using a thread"
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()

    def stop(self):
        "Finishes the audio recording therefore the thread too"
        if self.open:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()

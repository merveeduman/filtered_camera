from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np
import time

class CameraThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = True
        self.cap = cv2.VideoCapture(0)
        self.last_time = time.time()
        self.frames = 0

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frames += 1
                self.frame_ready.emit(frame)
                time.sleep(0.03)
                self.calculate_fps()
        self.cap.release()

    def stop(self):
        self.running = False

    def calculate_fps(self):
        current_time = time.time()
        fps = self.frames / (current_time - self.last_time)
        self.last_time = current_time
        self.frames = 0
        return fps




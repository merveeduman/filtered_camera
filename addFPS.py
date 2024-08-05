import sys
import cv2
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSlot
from camera import CameraThread
from datetime import datetime

class FilteredCamera(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('filtered_camera.ui', self)

        self.lbl_normal = self.findChild(QLabel, 'lbl_normal')
        self.lbl_red_filter = self.findChild(QLabel, 'lbl_red_filter')
        self.lbl_green_filter = self.findChild(QLabel, 'lbl_green_filter')
        self.lbl_blue_filter = self.findChild(QLabel, 'lbl_blue_filter')
        self.btn_baslat = self.findChild(QPushButton, 'btn_baslat')
        self.btn_bitir = self.findChild(QPushButton, 'btn_bitir')

        self.btn_baslat.clicked.connect(self.on_start_filters)
        self.btn_bitir.clicked.connect(self.on_stop_filters)

        self.filters_active = False
        self.camera_thread = None

    def on_start_filters(self):
        print("Filtreleme başlıyor")
        if self.camera_thread is None or not self.camera_thread.isRunning():
            self.filters_active = True
            self.camera_thread = CameraThread()
            self.camera_thread.frame_ready.connect(self.update_frame)
            self.camera_thread.start()
            print("CameraThread başlatıldı")

    def on_stop_filters(self):
        print("Filtreleme bitti")
        if self.camera_thread is not None:
            self.filters_active = False
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.clear_filters()
            self.camera_thread = None
            print("CameraThread durduruldu")

    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        if self.filters_active:
            height, width, _ = frame.shape
            top_left = frame[:height // 2, :width // 2]
            top_right = frame[:height // 2, width // 2:]
            bottom_left = frame[height // 2:, :width // 2]
            bottom_right = frame[height // 2:, width // 2:]

            red_filter = top_right.copy()
            red_filter[:, :, 1:] = 0

            green_filter = bottom_left.copy()
            green_filter[:, :, [0, 2]] = 0

            blue_filter = bottom_right.copy()
            blue_filter[:, :, :2] = 0


            if self.lbl_normal:
                fps = self.camera_thread.calculate_fps()
                self.draw_text(top_left, f"FPS: {fps:.2f}", (10, 30), (0, 255, 0))
                self.update_label_image(self.lbl_normal, top_left)


            if self.lbl_blue_filter:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.draw_text(blue_filter, current_time, (width - 300, 30), (0, 255, 255))
                self.update_label_image(self.lbl_blue_filter, blue_filter)


            if self.lbl_red_filter:
                self.update_label_image(self.lbl_red_filter, red_filter)
            if self.lbl_green_filter:
                self.update_label_image(self.lbl_green_filter, green_filter)

    def draw_text(self, image, text, position, color):
        cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    def clear_filters(self):
        height, width = 480, 640
        blank_image = np.zeros((height, width, 3), dtype=np.uint8)
        self.update_label_image(self.lbl_normal, blank_image)
        self.update_label_image(self.lbl_red_filter, blank_image)
        self.update_label_image(self.lbl_green_filter, blank_image)
        self.update_label_image(self.lbl_blue_filter, blank_image)

    def update_label_image(self, label, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, _ = image_rgb.shape
        bytes_per_line = 3 * width
        q_image = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        label.setPixmap(pixmap)

    def closeEvent(self, event):
        if self.camera_thread is not None:
            self.camera_thread.stop()
            self.camera_thread.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FilteredCamera()
    ex.show()
    sys.exit(app.exec_())

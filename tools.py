import sys
import os
import ctypes
from PIL import ImageGrab, Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWinExtras import QtWin
from time import sleep

# 配置
CONFIG_PATH = os.path.join(os.getcwd(), 'gc.txt')
RELOAD_INTERVAL = 100  # ms


class Box:
    def __init__(self, x, y, size):
        self.rect = QtCore.QRect(x, y, size, size)
        self.color = QtGui.QColor(0, 255, 0)

    def draw(self, painter):
        pen = QtGui.QPen(QtGui.QColor(0, 255, 0))  # 绿色字体
        painter.setPen(pen)

        font = QtGui.QFont()
        font.setPointSize(12)  # 加大字体
        font.setBold(True)
        painter.setFont(font)

        painter.drawRect(self.rect)



class OverlayWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        # 全屏覆盖
        desktop = QtWidgets.QApplication.desktop()
        self.setGeometry(desktop.geometry())

        # 点击穿透
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x80000
        WS_EX_TRANSPARENT = 0x20
        WS_EX_TOOLWINDOW = 0x80
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

        # 加载框配置与模型
        self.box_objects = []
        self.load_config()

        # 定时重载配置
        self.reload_timer = QtCore.QTimer()
        self.reload_timer.timeout.connect(self.on_reload)
        self.reload_timer.start(RELOAD_INTERVAL)


    def load_config(self):
        boxes = []
        if not os.path.exists(CONFIG_PATH):
            self.box_objects = boxes
            return
        try:
            with open(CONFIG_PATH, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = [float(p) for p in line.split(',')]
                    x0, y0, h_spacing, h_count, v_spacing, v_count, box_size = parts
                    box_size = round(box_size)
                    for i in range(int(v_count)):
                        for j in range(int(h_count)):
                            x = round(x0 + j * h_spacing - box_size / 2 + 32)
                            y = round(y0 + i * v_spacing - box_size / 2 + 32)
                            boxes.append(Box(x, y, box_size))
        except Exception as e:
            print(f"Error reading config: {e}")
        self.box_objects = boxes

    @QtCore.pyqtSlot()
    def on_reload(self):
        #self.load_config()
        self.update()

    @QtCore.pyqtSlot()
    def detect_boxes(self):
        if not self.box_objects:
            return

        self.hide()
        QtWidgets.QApplication.processEvents()
        sleep(0.01)
        screen = ImageGrab.grab()
        self.show()
        QtWidgets.QApplication.processEvents()

        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        for box in self.box_objects:
            box.draw(painter)
        painter.end()


if __name__ == '__main__':
    print("[INFO] Overlay started. Press ESC to quit if implemented.")
    app = QtWidgets.QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    sys.exit(app.exec_())

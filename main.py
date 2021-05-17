# -*- coding:utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
import win32gui
import win32con

from MainWindow import MainWindow


# 将窗口置顶
def to_top():
    hwnd = win32gui.FindWindow(None, 'BulletWindow')
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOOWNERZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW | win32con.SWP_NOSIZE)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    # mainWindow.bulletWindow.show()
    # 定时将窗口置顶一次
    timer = QTimer()
    timer.timeout.connect(to_top)
    timer.start(500)
    sys.exit(app.exec_())

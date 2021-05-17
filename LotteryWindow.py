# -*- coding:utf-8 -*-
import time

import win32con
from PyQt5.QtCore import Qt, QThread, QPropertyAnimation
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QBrush, QPainter, QPainterPath, QColor, QFont, QPen, QFontMetrics
import win32gui


class Lottery(QLabel):
    weightDefault = 100
    sizeDefault = 280
    fontDefault = "黑体"
    font = QFont(fontDefault, sizeDefault, weightDefault)
    color = QColor(255, 0, 0)

    def __init__(self, parent, text):
        super(Lottery, self).__init__(parent)
        self.content = str(text)
        self.setText(self.content)
        self.metrics = QFontMetrics(self.font)
        self.height = self.metrics.height() + 5
        self.setFixedHeight(self.height)
        self.width = self.metrics.width("1111111111") * 1.2
        self.setFixedWidth(self.width)
        self.setFont(self.font)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color:" + self.color.name())
        self.move(parent.width() / 2 - self.width / 2, parent.height() / 4 - self.height / 2)


class LotteryWindow(QWidget):

    def __init__(self, parent):
        super(LotteryWindow, self).__init__(parent)
        self.width = QDesktopWidget().screenGeometry().width()  # 弹幕宽度
        self.height = QDesktopWidget().screenGeometry().height()  # 屏幕高度
        self.setFixedSize(self.width, self.height)  # 将窗口最大化
        self.setWindowTitle('LotteryWindow')  # 窗口名称
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 窗口透明
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)  # 窗口始终保持最前且不显示边框且任务栏不显示
        self.setEnabled(False)
        self.qw = QWidget(self)
        self.qw.setFixedSize(self.width, self.height)
        # 设置鼠标穿透
        win32gui.SetWindowLong(self.winId(), win32con.GWL_EXSTYLE, win32gui.GetWindowLong(self.winId(),
                                                                                          win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
        self.show()

# -*- coding:utf-8 -*-
import time

import win32con
from PyQt5.QtCore import Qt, QThread, QPropertyAnimation
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QBrush, QPainter, QPainterPath, QColor, QFont, QPen, QFontMetrics
import win32gui


class Bullet(QLabel):
    transparencyDefault = 100
    weightDefault = 75
    sizeDefault = 25
    fontDefault = "黑体"
    font = QFont(fontDefault, sizeDefault, weightDefault)
    color = QColor(255, 255, 255)
    duration = 10  # 秒数

    def __init__(self, parent, screen_index, text, y_index, is_animation):
        super(Bullet, self).__init__(parent)
        if is_animation:
            self.setVisible(False)
        self.setStyleSheet("color:rgba(255,255,255,0)")  # 颜色全透明，避免描边出现错位
        self.content = str(text)
        self.setText(self.content)
        self.metrics = QFontMetrics(self.font)
        try:
            self.setGeometry(50, 500, 600, 70)
        except Exception as e:
            print(e)
        self.height = self.metrics.height() + 5
        self.setFixedHeight(self.height)
        self.width = self.metrics.width(self.content) * 1.2
        self.setFixedWidth(self.width)
        self.setFont(self.font)

        if is_animation:
            self.y_index = y_index  # 起始高度
            self.fly = QPropertyAnimation(self, b'pos')  # 弹幕飞行动画
            self.fly.setDuration(self.duration * 1000)
            self.fly.setStartValue(QtCore.QPoint(QDesktopWidget().screenGeometry(screen_index).width(), self.y_index))
            self.fly.setEndValue(QtCore.QPoint(0 - self.width, self.y_index))
            self.setVisible(True)
            self.fly.start()
            self.fly.finished.connect(self.deleteLater)

    # 为文字添加描边
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.save()
        path = QPainterPath()
        pen = QPen(QColor(0, 0, 0, 230))
        painter.setRenderHint(QPainter.Antialiasing)  # 反走样
        pen.setWidth(2)
        length = self.metrics.width(self.content)
        w = self.width
        px = (length - w) / 2
        if px < 0:
            px = -px
        py = (self.height - self.metrics.height()) / 2 + self.metrics.ascent()
        if py < 0:
            py = -py
        path.addText(px - 2, py, self.font, self.content)
        painter.strokePath(path, pen)
        painter.drawPath(path)
        painter.fillPath(path, QBrush(self.color))
        painter.restore()
        QLabel.paintEvent(self, event)


class BulletWindow(QWidget):
    screen_ratio = 0.6  # 屏占比
    bullet_interval = 1.1  # 弹幕间隔比例

    def __init__(self, parent):
        super(BulletWindow, self).__init__(parent)
        self.screenIndex = 0
        self.width = QDesktopWidget().screenGeometry().width()  # 弹幕宽度
        self.height = QDesktopWidget().screenGeometry().height()  # 屏幕高度
        self.bulletHeight = int(QDesktopWidget().screenGeometry().height() * self.screen_ratio)  # 弹幕高度
        self.__track_width = 20  # 弹幕单位轨道宽20
        self.__total_track = int(QDesktopWidget().screenGeometry().height() / self.__track_width)  # 轨道数
        self.__track_record = [{"accessible": True, "time": 0.0, "away_time": 0.0} for _ in range(self.__total_track)]
        self.setFixedSize(self.width, self.height)  # 将窗口最大化
        self.setWindowTitle('BulletWindow')  # 窗口名称
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 窗口透明
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)  # 窗口始终保持最前且不显示边框且任务栏不显示
        self.setEnabled(False)
        self.qw = QWidget(self)
        self.qw.setFixedSize(self.width, self.height)
        # self.qb = QVBoxLayout(self.qw)  # TODO 解决卡顿问题
        # 设置鼠标穿透
        win32gui.SetWindowLong(self.winId(), win32con.GWL_EXSTYLE, win32gui.GetWindowLong(self.winId(),
                                                                                          win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
        self.show()

    def add_bullet(self, message):
        height = self.get_y_index(message)
        if height == -1:
            return
        Bullet(self.qw, self.screenIndex, message, height, True)

    def get_y_index(self, message):
        fontHeight = QFontMetrics(Bullet.font).height() * 1.05
        fontWidth = QFontMetrics(Bullet.font).width(message)
        awayTime = Bullet.duration / float(self.width + fontWidth) * fontWidth * self.bullet_interval
        track = self.find_track(fontHeight)
        if track == -1:
            return -1
        self.set_track(track, fontHeight, awayTime)
        return track * self.__track_width

    def find_track(self, height):
        i = 0
        while i * self.__track_width < self.bulletHeight:
            if self.is_valid_track(i, height):
                return i
            i = i + 1
        return -1

    def is_valid_track(self, track_index, height):
        i = 0
        while i * self.__track_width < height and track_index + i < self.__total_track:
            if not self.__track_record[track_index + i]["accessible"] and self.__track_record[track_index + i]["away_time"] + self.__track_record[track_index + i]["time"] > time.time():
                return False
            i = i + 1
        return True

    def set_track(self, track_index, height, away_time):
        i = 0
        while i * self.__track_width < height:
            self.__track_record[track_index + i]["accessible"] = False
            self.__track_record[track_index + i]["time"] = time.time()
            self.__track_record[track_index + i]["away_time"] = away_time
            i = i + 1

    def switch_screen(self, screen_index):
        self.screenIndex = screen_index
        self.setGeometry(QDesktopWidget().screenGeometry(screen_index))
        self.width = QDesktopWidget().screenGeometry(screen_index).width()  # 弹幕宽度
        self.height = QDesktopWidget().screenGeometry(screen_index).height()  # 屏幕高度
        self.bulletHeight = int(QDesktopWidget().screenGeometry(screen_index).height() * self.screen_ratio)  # 弹幕高度
        self.setFixedSize(self.width, self.height)  # 将窗口最大化
        self.qw.setFixedSize(self.width, self.height)

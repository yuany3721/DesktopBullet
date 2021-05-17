# -*- coding:utf-8 -*-
import random

from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QColor, QTextCursor, QFontMetrics
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation
import threading
import json
import os.path
import time

from BulletWindow import BulletWindow, Bullet
from LotteryWindow import LotteryWindow, Lottery
from WebSocket import WebSocket


# 获取ttf
def get_ttf():
    qFontDatabase = QFontDatabase()
    return qFontDatabase.families(QFontDatabase.SimplifiedChinese)


# 从持续时间获取飞行速度
def get_speed(duration_time):
    return 100 - (duration_time - 2) * 10


# 弹幕控制窗口
class BulletWidget(QWidget):

    def __init__(self, parent):
        super(BulletWidget, self).__init__(parent)
        self.setFixedSize(parent.width(), parent.height())  # 设置窗口大小

        # 透明度
        self.transparencyLabel = QLabel("弹幕透明度", self)
        self.transparencyLabel.setStyleSheet("font-size:20px")
        self.transparencyLabel.move(300, 30)
        self.transparencyMax = QLabel(str(Bullet.transparencyDefault), self)
        self.transparencyMax.move(555, 35)
        self.transparencySlider = QSlider(Qt.Horizontal, self)
        self.transparencySlider.move(400, 30)
        self.transparencySlider.setFixedSize(150, 20)
        self.transparencySlider.setRange(0, 100)
        self.transparencySlider.setValue(Bullet.transparencyDefault)
        self.transparencySlider.valueChanged.connect(self.transparency_change)

        # 字体粗细
        self.weightLabel = QLabel("弹幕粗细", self)
        self.weightLabel.setStyleSheet("font-size:20px")
        self.weightLabel.move(300, 60)
        self.weightMax = QLabel(str(Bullet.weightDefault), self)
        self.weightMax.move(555, 65)
        self.weightSlider = QSlider(Qt.Horizontal, self)
        self.weightSlider.move(400, 60)
        self.weightSlider.setFixedSize(150, 20)
        self.weightSlider.setRange(20, 127)
        self.weightSlider.setValue(Bullet.weightDefault)
        self.weightSlider.valueChanged.connect(self.weight_change)

        # 字体大小
        self.sizeLabel = QLabel("弹幕大小", self)
        self.sizeLabel.setStyleSheet("font-size:20px")
        self.sizeLabel.move(300, 90)
        self.sizeMax = QLabel(str(Bullet.sizeDefault), self)
        self.sizeMax.move(555, 95)
        self.sizeSlider = QSlider(Qt.Horizontal, self)
        self.sizeSlider.move(400, 90)
        self.sizeSlider.setFixedSize(150, 20)
        self.sizeSlider.setRange(5, 127)
        self.sizeSlider.setValue(Bullet.sizeDefault)
        self.sizeSlider.valueChanged.connect(self.size_change)

        # 弹幕速度
        self.durationLabel = QLabel("弹幕速度", self)
        self.durationLabel.setStyleSheet("font-size:20px")
        self.durationLabel.move(300, 120)
        self.durationMax = QLabel(str(get_speed(Bullet.duration)), self)
        self.durationMax.move(555, 125)
        self.durationSlider = QSlider(Qt.Horizontal, self)
        self.durationSlider.move(400, 120)
        self.durationSlider.setFixedSize(150, 20)
        self.durationSlider.setRange(0, 100)
        self.durationSlider.setValue(get_speed(Bullet.duration))
        self.durationSlider.valueChanged.connect(self.duration_change)

        # 字体
        self.fontFamilySelector = QComboBox(self)
        self.fontFamilySelector.move(365, 160)
        self.fontFamilySelector.setFixedSize(200, 50)
        self.fontFamilySelector.addItems(get_ttf())
        self.fontFamilySelector.setCurrentText(Bullet.fontDefault)
        self.font_family_selector_change()
        self.fontFamilySelector.currentTextChanged.connect(self.font_family_selector_change)
        self.fontFamily = QLabel("字体", self)
        self.fontFamily.setStyleSheet("font-size:20px")
        self.fontFamily.move(300, 170)

        # 选择颜色
        self.colorSelectorButton = QPushButton("选择颜色", self)
        self.colorSelectorButton.move(365, 220)
        self.colorSelectorButton.setFixedSize(120, 50)
        self.colorSelectorButton.clicked.connect(self.color_selector_change)
        self.fontColor = QLabel("颜色", self)
        self.fontColor.setStyleSheet("font-size:20px")
        self.fontColor.move(300, 230)

        self.bulletWindow = BulletWindow(self)  # 创建弹幕窗口

        self.show()

    # 透明度改变事件
    def transparency_change(self, event):
        self.transparencyMax.setText(str(self.transparencySlider.value()))
        self.bulletWindow.setWindowOpacity(self.transparencySlider.value() / 100)

    # 粗细改变事件
    def weight_change(self):
        self.weightMax.setText(str(self.weightSlider.value()))
        Bullet.font.setWeight(self.weightSlider.value())

    # 大小改变事件
    def size_change(self):
        self.sizeMax.setText(str(self.sizeSlider.value()))
        Bullet.font.setPointSize(self.sizeSlider.value())

    # 飞行时间改变事件
    def duration_change(self):
        duration_time = 2 + int((100 - self.durationSlider.value()) / 10)
        self.durationMax.setText(str(self.durationSlider.value()))
        Bullet.duration = duration_time

    # 字体改变事件
    def font_family_selector_change(self):
        # fontName = QFontDatabase.applicationFontFamilies(self.fontFamilySelector.currentIndex())[0]
        fontThis = QFont(self.fontFamilySelector.currentText())
        self.fontFamilySelector.setFont(fontThis)
        Bullet.font.setFamily(self.fontFamilySelector.currentText())

    # 颜色改变事件
    def color_selector_change(self):
        # print(123)
        color = QColorDialog.getColor()
        if color.name() == "#000000":
            return
        Bullet.color = QColor(color.name())
        self.colorSelectorButton.setStyleSheet("background-color:" + color.name())
        self.colorSelectorButton.setText(color.name())

    def handle(self, qq, content):
        self.bulletWindow.add_bullet(content)


# 抽奖窗口
class LotteryWidget(QWidget):

    def __init__(self, parent):
        super(LotteryWidget, self).__init__(parent)
        self.setFixedSize(parent.width(), parent.height())  # 设置窗口大小
        self.parent = parent
        self.lotteryList = []   # 有抽奖资格的列表
        self.bakList = []    # 清空备份列表
        self.showNum = 5    # 抽奖列表显示行数
        self.showFont = "Consolas"  # 抽奖列表字体
        self.showPointSize = 25  # 抽奖列表字体大小
        self.showWeight = 20  # 抽奖列表字体粗细

        # 抽奖列表
        self.lotteryLabel = QLabel("抽奖资格列表 当前人数：" + str(len(self.lotteryList)), self)
        self.lotteryLabel.setStyleSheet("font-size:" + str(self.showPointSize-5) + "px;font-family:" + self.showFont + ";")
        self.lotteryMember = QTextEdit(self)
        self.lotteryMember.move(320, 50)
        fontMetrics = QFontMetrics(QFont(self.showFont, self.showPointSize, self.showWeight))       # 获取单行宽高
        self.lotteryMember.setFixedSize(fontMetrics.width("111111111111"), self.showNum * fontMetrics.height() + 5)
        self.lotteryLabel.move(320 + fontMetrics.width("11111111111") / 2 - fontMetrics.width("抽奖资格列表") / 2, 20)
        self.lotteryMember.setFontFamily(self.showFont)
        self.lotteryMember.setFontPointSize(self.showPointSize)
        self.lotteryMember.setFontWeight(self.showWeight)
        self.lotteryMember.setAlignment(Qt.AlignCenter)     # 文字居中
        self.lotteryMember.setReadOnly(True)

        self.lotteryButton = QPushButton("开始", self)
        self.lotteryButton.move(320, 75 + self.lotteryMember.height())
        self.lotteryButton.setFixedSize(100, 50)
        self.lotteryButton.clicked.connect(self.lottery)
        self.lotteryButton.setEnabled(False)        # 初始禁用
        self.clearButton = QPushButton("清空", self)
        self.clearButton.move(440, 75 + self.lotteryMember.height())
        self.clearButton.setFixedSize(100, 50)
        self.clearButton.clicked.connect(self.clear_list)
        self.clearButton.setEnabled(False)        # 初始禁用
        self.lotteryWindow = LotteryWindow(self)
        self.lotteryInfoLabel = Lottery(self.lotteryWindow.qw, "")
        self.timer = QTimer()
        self.timer.timeout.connect(self.lottery_info_change)
        self.show()

    def handle(self, qq, content="default"):
        if self.lotteryButton.text() == "停止":
            return
        try:
            if "测试" in content:
                return
            longQQ = int(qq)
        except Exception as e:
            return
        if str(longQQ) in self.lotteryList:
            return
        self.lotteryMember.append(str(longQQ))
        self.lotteryList.append(str(longQQ))
        self.lotteryLabel.setText("抽奖资格列表 当前人数：" + str(len(self.lotteryList)))
        self.lotteryButton.setEnabled(True)
        self.clearButton.setText("清空")
        self.clearButton.setEnabled(True)

    def lottery(self):
        if self.lotteryButton.text() == "开始":
            self.lotteryInfoLabel.setVisible(True)
            self.lotteryButton.setEnabled(False)
            self.lotteryButton.repaint()
            self.clearButton.setEnabled(False)
            self.clearButton.repaint()
            self.lotteryButton.setText("停止")
            for _ in range(5):
                self.lottery_info_change()
                time.sleep(0.5)
            self.timer.start(100)
            self.lotteryButton.setEnabled(True)
        else:
            self.lotteryButton.setEnabled(False)
            self.lotteryButton.repaint()
            self.timer.stop()
            for _ in range(5):
                self.lottery_info_change()
                time.sleep(0.5)
            self.parent.heartbeat("lottery:" + self.lotteryInfoLabel.text())
            self.lotteryButton.setText("开始")
            self.lotteryButton.setEnabled(True)
            self.timer.singleShot(7500, self.clear_info)
            self.clearButton.setEnabled(True)
        pass

    def lottery_info_change(self):
        text = self.lotteryList[random.randint(0, len(self.lotteryList)-1)]
        # print(text)
        self.lotteryInfoLabel.setText(text)
        self.lotteryInfoLabel.repaint()

    def clear_info(self):
        self.lotteryInfoLabel.setText("")
        self.lotteryInfoLabel.setVisible(False)

    def clear_list(self):
        if self.clearButton.text() == "清空":
            self.bakList = self.lotteryList.copy()
            self.lotteryList.clear()
            self.lotteryMember.clear()
            self.lotteryMember.setAlignment(Qt.AlignCenter)
            self.lotteryLabel.setText("抽奖资格列表 当前人数：" + str(len(self.lotteryList)))
            self.clearButton.setText("还原")
            self.clearButton.repaint()
            self.lotteryButton.setEnabled(False)
        else:
            self.clearButton.setText("清空")
            for item in self.bakList:
                self.handle(item)


class MainWindow(QMainWindow):
    bulletSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.bulletWidget = BulletWidget(self)     # 弹幕部分
        self.lotteryWidget = LotteryWidget(self)       # 抽奖部分
        self.widgets = ["弹幕", "抽奖"]        # widget集合
        self.isShow = -1      # 显示的widget

        # 服务器地址
        # self.server = "ws://localhost:8087/connect"  # 本地测试
        self.server = "ws://yuany3721.top:8087/connect"     # 生产环境
        self.beat_interval = 60  # 心跳发送间隔（s）
        self.setWindowTitle("桌面弹幕")  # 窗口名
        self.setWindowIcon(QIcon("favicon.ico"))  # 窗口图标
        self.setFixedSize(600, 360)  # 设置窗口大小
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint)  # 标题栏仅显示关闭按钮

        # 连接服务器
        self.connectButton = QPushButton("连接服务器", self)
        self.connectButton.setStyleSheet("font-size:30px")
        self.connectButton.setObjectName("connectButton")
        self.connectButton.move(25, 25)
        self.connectButton.setFixedSize(200, 75)
        self.connectButton.clicked.connect(self.connect_server)
        self.connectStatusLabel = QLabel("当前状态: 未连接", self)
        self.connectStatusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.connectStatusLabel.setStyleSheet("font-size:20px")
        self.connectStatusLabel.move(25, 95)
        self.connectStatusLabel.setFixedSize(200, 50)

        # 最小化到托盘
        self.miniButton = QPushButton("最小化到托盘", self)
        self.miniButton.move(25, 150)
        self.miniButton.setFixedSize(200, 75)
        self.miniButton.clicked.connect(self.hide_window)

        # 任务栏图标
        self.sysIcon = QSystemTrayIcon(self)
        icon = QIcon("favicon.ico")
        self.sysIcon.setIcon(icon)
        self.sysIcon.setToolTip("桌面弹幕")
        self.sysIcon.activated.connect(self.on_activated)

        # qss加载
        with open(os.path.join(os.getcwd(), "style.qss")) as f:
            style = f.read()
        self.setStyleSheet(style)

        # 切换功能
        self.switchButton = QPushButton("功能切换", self)
        self.switchButton.setStyleSheet("font-size:25px")
        self.switchButton.setObjectName("switchButton")
        self.switchButton.move(25, 250)
        self.switchButton.setFixedSize(200, 50)
        self.switchButton.clicked.connect(self.switch)
        self.switch()

        self.show()  # 显示界面

        self.bulletSignal.connect(self.handle)  # 信号连接
        self.ws = WebSocket(self.server, self)  # webSocket服务器

        # 心跳
        self.beat_timer = QTimer()
        self.beat_timer.timeout.connect(self.heartbeat)
        self.beat_timer.start(self.beat_interval * 1000)
        self.longlong = 1111111111

    # 连接服务器
    def connect_server(self):
        try:
            self.connectButton.setEnabled(False)
            self.threading = threading.Thread(target=self.connect)
            self.threading.setDaemon(True)
            self.threading.start()
        except Exception as err:
            print(err)
        self.connectButton.setEnabled(True)

    def connect(self):
        if self.connectStatusLabel.text() == "当前状态：已连接":
            print("disconnecting to: " + self.server)
            self.connectButton.setText("断开连接中")
            try:
                self.ws.close(1000, "主动关闭连接")
                self.connectStatusLabel.setText("当前状态：已断开连接")
                self.connectButton.setText("连接服务器")
            except Exception as e:
                print(e)
        else:
            print("connecting to: " + self.server)
            self.connectButton.setText("连接中")
            try:
                if self.ws.__getattribute__("connection") is None:
                    self.ws = WebSocket(self.server, self)  # 说明close过
                self.ws.connect()
                self.connectStatusLabel.setText("当前状态：已连接")
                self.heartbeat()
                self.connectButton.setText("断开连接")
                self.ws.run_forever()
            except Exception as e:
                print(e)
                self.connectStatusLabel.setText("当前状态：连接失败")
                self.connectButton.setText("连接服务器")

    # 心跳
    def heartbeat(self, message="heartbeat"):
        if not self.connectStatusLabel.text() == "当前状态：已连接":
            return
        try:
            self.ws.send(message)
        except Exception as err:
            self.connectStatusLabel.setText("当前状态：连接失败")
            self.connectButton.setText("连接服务器")
            self.connectButton.setEnabled(True)
            print(err)

    # 接收到信号后的处理
    def handle(self, message):
        # print(message)
        if "+-+-+" in message:
            qq = message.split("+-+-+")[0]
            content = message.split("+-+-+")[1]
            if self.widgets[self.isShow] == "弹幕":
                self.bulletWidget.handle(qq, content)
            elif self.widgets[self.isShow] == "抽奖":
                self.lotteryWidget.handle(qq, content)
        elif "lottery:invalid#" in message:
            self.bulletWidget.bulletWindow.add_bullet(message.split("#")[1] + "好像不在群里，这次抽奖可能无效哟~")
        elif "lottery:valid#" in message:
            self.bulletWidget.bulletWindow.add_bullet("恭喜" + message.split("#")[1] + "中奖！")
        else:
            print("info message: " + message)

    # 切换widget显示
    def switch(self):
        self.isShow = (self.isShow + 1) % len(self.widgets)
        self.switchButton.setText("当前功能：" + self.widgets[self.isShow])
        self.bulletWidget.setVisible("弹幕" == self.widgets[self.isShow])
        self.lotteryWidget.setVisible("抽奖" == self.widgets[self.isShow])
        self.lotteryWidget.lotteryInfoLabel.setVisible("抽奖" == self.widgets[self.isShow])

    # 最小化到任务栏
    def hide_window(self):
        self.hide()
        self.sysIcon.show()

    # 任务栏点击
    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason(QSystemTrayIcon.Trigger):
            self.show()
            self.sysIcon.hide()

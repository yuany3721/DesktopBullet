# -*- coding:utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient


class WebSocket(WebSocketClient):
    def __init__(self, url, parent):
        super().__init__(url)
        self.parent = parent

    def opened(self):
        print('webSocket connected')

    def received_message(self, message):
        self.parent.bulletSignal.emit(str(message))

    def closed(self, code=1000, reason=''):
        print('webSocket closed')

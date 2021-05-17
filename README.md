# DesktopBullet
山西大学经济与管理学院2021届本科生毕业晚会桌面弹幕客户端

[弹幕后台地址](https://github.com/yuany3721/BulletWSServer)

Base on PyQt5 for Python

## Before Usage
修改 `MainWindow.py` 中 `class MainWindow` 的 `self.server` 为你自己的弹幕服务端WebSocket地址 

## Usage
```shell script
python main.py
````

## Package
```shell script
pyinstaller --hidden-import=queue -F -w -i favicon.ico main.py
```

Then copy `favicon.ico` and `style.qss` into `dist`, and run `main.exe`


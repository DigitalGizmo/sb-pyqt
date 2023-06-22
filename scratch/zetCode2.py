#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we show how to
emit a custom signal.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QApplication


class StartupSender(QObject):

    # closeApp = pyqtSignal()
    startPressed = pyqtSignal()


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.startUpObject = StartupSender()
        self.startUpObject.startPressed.connect(self.printThis)

        self.setGeometry(300, 300, 450, 350)
        self.setWindowTitle('Emit signal')
        self.show()

    def mousePressEvent(self, event):

        self.startUpObject.startPressed.emit()
    
    def printThis(self):
        print("make first call")


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
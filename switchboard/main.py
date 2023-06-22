import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import vlc
import json

contentJsonFile = open('conversations.json')
contentPy = json.load(contentJsonFile)

class MainWindow(QMainWindow): 
    # Almost all of this should be in separate module analogous to svelte Panel
    def __init__(self):
        # self.pygame.init()
        super().__init__()

        self.setWindowTitle("You Are the Operator")
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setText("Keep your ears open for incoming calls!")
        self.label.setAlignment(Qt.AlignTop)
        # self.label.setStyleSheet("vertical-align: top;")
        self.setWindowTitle("You're the Operator")
        self.setGeometry(20,120,600,200)
        self.setCentralWidget(self.label)

        self.buzzer = vlc.MediaPlayer("/home/pi/apps/sb-pyqt/audio/buzzer.wav")

    def mousePressEvent(self,e):
        self.label.setText("Keep your ears open for incoming calls")
        # Audio
        self.buzzer.play()
        # self.blinkTimer.start(500)
        # test
        SBLogic.handlePlugIn()


class SBLogic():
    def handlePlugIn():
        print('got to handle plugin')

app = QApplication([])

win = MainWindow()
win.show()

sys.exit(app.exec_())
import sys
from random import choice
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

window_titles = [
    'My App',
    'My App',
    'still My app',
    'still My app',
    'What on earth',
    'What on earth',
    'special title'
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.button_is_checked = True
        self.n_times_clicked = 0

        self.setWindowTitle("You Are the Operator")
        # self.window.setGeometry(100,100,280,80)

        self.button = QPushButton("push me")
        self.button.clicked.connect(self.the_button_was_clicked)

        self.windowTitleChanged.connect(self.the_window_title_changed)

        self.setCentralWidget(self.button)

    # def mousePressEvent(self,e):
    #     self.label.setText("mouse press event")

    def the_button_was_clicked(self):
        print("Clicked")
        new_window_title = choice(window_titles)
        print("setting title: %s" % new_window_title)
        self.setWindowTitle(new_window_title)

    def the_window_title_changed(self, window_title):
        print("window title changed: %s" % window_title)

        if window_title == 'special title':
            self.button.setDisabled(True)



app = QApplication([])

win = MainWindow()
win.show()

sys.exit(app.exec_())
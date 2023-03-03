import sys
import time
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.button_is_checked = True

        self.setWindowTitle("You Are the Operator")
        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setText("Lorem")
        # self.label.setText("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum")
        # self.button = QPushButton("push me")
        # button.setCheckable(True)
        # self.button.clicked.connect(self.the_button_was_clicked)
        # button.clicked.connect(self.the_button_was_toggled)
        # button.setChecked(self.button_is_checked)

        # layout = QVBoxLayout()
        # layout.addWidget(self.label)

        # container = QWidget()
        # container.setLayout(layout)
    
        self.setFixedSize(QSize(400, 300))

        # self.setCentralWidget(container)
        self.setCentralWidget(self.label)

    def mousePressEvent(self,e):
        self.label.setText("to be counted")
        self.counter()

    # def the_button_was_clicked(self):
    #     # print("Clicked")
    #     self.button.setText("already clicked")
    #     self.button.setEnabled(False)

    #     self.setWindowTitle("please aswer")

    # def the_button_was_toggled(self, checked):
    #     self.button_is_checked = checked

    #     print("Checked??", self.button_is_checked)

    def counter(self):
        count = 0
        while count < 3:
            self.label.setText("count: " + str(count))
            count += 1
            # time.sleep(1)




app = QApplication([])

win = MainWindow()
win.show()

sys.exit(app.exec_())
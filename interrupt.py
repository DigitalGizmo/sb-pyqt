import sys
# import time
# import asyncio
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
import board
import busio
from digitalio import Direction, Pull
from RPi import GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.button_is_checked = True
        self.count = 0

        self.setWindowTitle("You Are the Operator")
        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setText("Lorem")
    

        self.timer=QTimer()
        self.timer.timeout.connect(self.counter)



        # Initialize the I2C bus:
        i2c = busio.I2C(board.SCL, board.SDA)

        mcp = MCP23017(i2c)

        # Make a list of all pins
        self.pins = []
        for pinIndex in range(0, 16):
            self.pins.append(mcp.get_pin(pinIndex))

        # Set 0 - 7 to output
        for pinIndex in range(0, 8):
            self.pins[pinIndex].switch_to_output(value=False)





        self.setFixedSize(QSize(400, 300))
        # self.setCentralWidget(container)
        self.setCentralWidget(self.label)

    def mousePressEvent(self,e):
        self.label.setText("to be counted")
        # self.counter()
        self.timer.start(1000)

    def counter(self):
        self.count += 1
        self.label.setText("count: " + str(self.count))
        self.pins[3].value = not self.pins[3].value
        # count = 0
        # while count < 3:
        #     self.label.setText("count: " + str(count))
        #     # time.sleep(1)




app = QApplication([])

win = MainWindow()
win.show()

sys.exit(app.exec_())
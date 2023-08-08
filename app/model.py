import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import vlc

import board
import busio
from digitalio import Direction, Pull
from RPi import GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017

class Model(qtc.QObject):
    displayText = qtc.pyqtSignal(str)
    # self.buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")
    # buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")

    def __init__(self):
        super().__init__()

        # The following possibly in veiw
        self.buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")
        self.blinkTimer=qtc.QTimer()
        self.blinkTimer.timeout.connect(self.blinker)

        # for control of LED
        i2c = busio.I2C(board.SCL, board.SDA)
        self.mcpLed = MCP23017(i2c, address=0x21)
        # LEDs which will detect 1st vs 2nd line
        self.pinsLed = []
        for pinIndex in range(0, 12):
            self.pinsLed.append(self.mcpLed.get_pin(pinIndex))
        # Set to output
        for pinIndex in range(0, 12):
           self.pinsLed[pinIndex].switch_to_output(value=False)


    def handlePlugIn(self, pluggedIdxInfo):
        """Main logic patterned after software proto
        """
        print(f"handlePlugIn: {pluggedIdxInfo}")

    def blinker(self):
        self.pinsLed[4].value = not self.pinsLed[4].value

    def handleStart(self):
        """Just for startup
        """
        print("start up")

        self.buzzer.play()
        self.blinkTimer.start(500)
        # self.pinsLed[4].value = not self.pinsLed[4].value
        # self.pinsLed[4].value = True

        self.displayText.emit("Start text for screen")


import sys
# import time
from random import choice
# import asyncio
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
import board
import busio
from digitalio import Direction, Pull
from RPi import GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017

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
        self.count = 0
        self.temp_window_count = 0
        self.blinking = True
        self.just_checked = False
        self.pinFlag = 0
        self.startBounceOnChange = False
        
        self.pins_in = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]
        self.names = ["zero","one","two","three","four","five","six","seven","eight","nine","ten","Charlie","Olive","thirteen"]

        self.setWindowTitle("You Are the Operator")
        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setText("Lorem")
    

        self.blinkTimer=QTimer()
        self.blinkTimer.timeout.connect(self.counter)

        self.bounceTimer=QTimer()
        # self.bounceTimer.setSingleShot(True)
        self.bounceTimer.timeout.connect(self.continueCheckPin)
        # QTimer.singleShot(500, lambda: continueCheckPin(pin_flag))

        self.windowTitleChanged.connect(self.the_window_title_changed)


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

        # Set 8 - 15 to input
        for pinIndex in range(8, 16):
            self.pins[pinIndex].direction = Direction.INPUT
            self.pins[pinIndex].pull = Pull.UP


        # Set up to check all the port B pins (pins 8-15) w/interrupts!
        # mcp.interrupt_enable = 0xFFFF  # Enable Interrupts in all pins
        mcp.interrupt_enable = 0xFF00  # Enable Interrupts in pins 8 - 15

        # If intcon is set to 0's we will get interrupts on
        # both button presses and button releases
        mcp.interrupt_configuration = 0x0000  # interrupt on any change
        mcp.io_control = 0x44  # Interrupt as open drain and mirrored
        # put this in Flask (startup)
        # mcp.clear_ints()  # Interrupts need to be cleared initially

        # connect either interrupt pin to the Raspberry pi's pin 17.
        # They were previously configured as mirrored.
        GPIO.setmode(GPIO.BCM)
        interrupt = 17
        GPIO.setup(interrupt, GPIO.IN, GPIO.PUD_UP)  # Set up Pi's pin as input, pull up



        def checkPin(port):
            """Callback function to be called when an Interrupt occurs."""
            for pin_flag in mcp.int_flag:
                # print("Interrupt connected to Pin: {}".format(port))
                print("Interrupt - pin number: {} changed to: {}".format(pin_flag,self.pins[pin_flag].value))
                
                if (pin_flag > 12): # if this is the short, stereo prong bein hit (first in, last out)
                    # await check_pin(pin_flag)
                    startCheckPin(pin_flag)

            mcp.clear_ints()

        def startCheckPin(pin_flag):
            # global just_checked
            # global pins_in
            if (not self.just_checked):
                # print('checking bcz false')
                self.just_checked = True

                self.pinFlag = pin_flag
                # self.bounceTimer.start(500)

                # trigger change that is detected to create an event in main thread
                self.temp_window_count += 1
                # new_window_title = choice(window_titles)
                # print("setting title: %s" % new_window_title)
                self.setWindowTitle("Window title: " + str(self.temp_window_count))

        GPIO.add_event_detect(interrupt, GPIO.BOTH, callback=checkPin, bouncetime=30)

        self.setFixedSize(QSize(400, 300))
        # self.setCentralWidget(container)
        self.setCentralWidget(self.label)


    def continueCheckPin(self):
        # print('in continueCheckPin, pin_flag: ' + str(self.pinFlag))
        # print('in continueCheckPin, pin_flag value: ' + str(self.pins[self.pinFlag].value))
        self.bounceTimer.stop()

        print("In continue, pinFlag-3 " + str(self.pinFlag-3) + " val " +
              str(self.pins[self.pinFlag-3].value))

        if (self.pins[self.pinFlag-3].value == False):
            print("Pin {} is now connected".format(self.pinFlag-3))

            # print("goint to check the following pin flag minus 3: " + str(self.pinFlag))

            # print("{} is now connected".format(self.names[self.pinFlagg-3]))
            if (self.pins[self.pinFlag].value == False):
                print("--- on line 2")
                
            # Set pin in
            self.pins_in[self.pinFlag-3] = True

            # stop flash
            if self.blinkTimer.isActive():
                self.blinkTimer.stop()

            # turn this LED on
            self.pins[self.pinFlag-11].value = True
            # Send msg to screen
            self.label.setText("Connected to {}  \n".format(self.names[self.pinFlag-3]))

        else:
            # Handle case of half-plugged -- where only stereo prong engaged
            # i.e. primary was never engaged
            if (self.pins_in[self.pinFlag-3]):
                # print("-- Pin {} has been disconnected \n".format(pin_flag-3))
                print("-- {} has been disconnected \n".format(self.names[self.pinFlag-3]))
                self.pins_in[self.pinFlag-3] = False
            else:
                print("got to pin true, but not pin in")

        # print('now setting true')
        self.just_checked = False

    def the_window_title_changed(self, window_title):
        print("window title changed so start bounceTimer: %s" % self.pinFlag)
        self.bounceTimer.start(500)

    def mousePressEvent(self,e):
        self.label.setText("to be counted, & change title")
        # self.counter()
        self.blinkTimer.start(1000)

    def counter(self):
        self.count += 1
        self.label.setText("count: " + str(self.count))
        self.pins[3].value = not self.pins[3].value


app = QApplication([])

win = MainWindow()
win.show()

sys.exit(app.exec_())
import sys
# import subprocess
# import time
# from random import choice
# import asyncio
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
# from PyQt5.QtMultimedia import QSound
# from playsound import playsound
# import pygame
from omxplayer.player import OMXPlayer
import board
import busio
from digitalio import Direction, Pull
from RPi import GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017



class MainWindow(QMainWindow): 
    def __init__(self):
        # self.pygame.init()
        super().__init__()
        self.count = 0
        self.temp_window_count = 0
        self.blinking = True
        self.just_checked = False
        self.pinFlag = 15
        self.startBounceOnChange = False
        self.pinsIn = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]
        self.names = ["zero","one","two","three","four","five","six","seven","eight","nine","ten","Charlie","Olive","thirteen"]
        self.setWindowTitle("You Are the Operator")
        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setText("Lorem")
        self.blinkTimer=QTimer()
        self.blinkTimer.timeout.connect(self.counter)
        self.buzzer = None
        self.incoming = None

        self.bounceTimer=QTimer()
        # self.bounceTimer.setSingleShot(True)
        self.bounceTimer.timeout.connect(self.continueCheckPin)
        # QTimer.singleShot(500, lambda: continueCheckPin(pin_flag))

        self.windowTitleChanged.connect(self.the_window_title_changed)

        # Initialize the I2C bus:
        i2c = busio.I2C(board.SCL, board.SDA)
        self.mcp = MCP23017(i2c)

        # Make a list of all pins
        self.pins = []
        for pinIndex in range(0, 16):
            self.pins.append(self.mcp.get_pin(pinIndex))
        # Set 0 - 7 to output
        for pinIndex in range(0, 8):
            self.pins[pinIndex].switch_to_output(value=False)

        # Set 8 - 15 to input
        for pinIndex in range(8, 16):
            self.pins[pinIndex].direction = Direction.INPUT
            self.pins[pinIndex].pull = Pull.UP

        # Set up to check all the port B pins (pins 8-15) w/interrupts!
        # mcp.interrupt_enable = 0xFFFF  # Enable Interrupts in all pins
        # self.mcp.interrupt_enable = 0xFF00  # Enable Interrupts in pins 8 - 15
        self.mcp.interrupt_enable = 0b0001111100000000  # Enable Interrupts in pins 8 - 12 aka 0x1f00

        # If intcon is set to 0's we will get interrupts on
        # both button presses and button releases
        self.mcp.interrupt_configuration = 0x0000  # interrupt on any change
        self.mcp.io_control = 0x44  # Interrupt as open drain and mirrored
        # put this in Flask (startup)
        self.mcp.clear_ints()  # Interrupts need to be cleared initially

        # connect either interrupt pin to the Raspberry pi's pin 17.
        # They were previously configured as mirrored.
        GPIO.setmode(GPIO.BCM)
        interrupt = 17
        GPIO.setup(interrupt, GPIO.IN, GPIO.PUD_UP)  # Set up Pi's pin as input, pull up

        def checkPin(port):
            """Callback function to be called when an Interrupt occurs."""
            for pin_flag in self.mcp.int_flag:
                # print("Interrupt connected to Pin: {}".format(port))
                # print("Interrupt pin_flag: {}".format(pin_flag))
                print("Interrupt - pin number: {} changed to: {} ".format(pin_flag,self.pins[pin_flag].value))
                
                # if (pin_flag < 13): # don't check the stereo prong on the way in

                if (not self.just_checked):
                    # print('checking bcz false')
                    self.just_checked = True
                    self.pinFlag = pin_flag
                    # trigger change that is detected to create an event in main thread
                    self.temp_window_count += 1
                    # new_window_title = choice(window_titles)
                    # print("setting title: %s" % new_window_title)
                    self.setWindowTitle("Window title: " + str(self.temp_window_count))

                # else: # stereo pin
                #     # check whether this was unplug. Stereo prong is engaged by the tip on the way out
                #     # There's only a few microseconds when the tip is disengaged before stereo prong
                #     # is also disengabed. So the tip change isn't detected
                #     # See if this is a stereo prong for a line that was engaged
                #     print("got to 13 or higher {}".format(self.pinFlag-3))
                #     if (self.pinsIn[self.pinFlag-3]):
                #         print("Looks like an unplug of {}".format(self.pinFlag-3))


        GPIO.add_event_detect(interrupt, GPIO.BOTH, callback=checkPin, bouncetime=100)

        self.setFixedSize(QSize(300, 200))
        # self.setCentralWidget(container)
        self.setCentralWidget(self.label)

    def continueCheckPin(self):
        # print('in continueCheckPin, pin_flag: ' + str(self.pinFlag))
        # print('in continueCheckPin, pin_flag value: ' + str(self.pins[self.pinFlag].value))
        self.bounceTimer.stop()

        print("In continue, pinFlag = " + str(self.pinFlag) + " val: " +
              str(self.pins[self.pinFlag].value))

        if (self.pins[self.pinFlag].value == False): # grounded by cable
            print("Pin {} is now connected".format(self.pinFlag))

            line = "line 1"

            print("Stereo pin {} aledgedly now: {}".format(self.pinFlag+3, self.pins[self.pinFlag+3].value))
            if (self.pins[self.pinFlag+3].value == True):
                line = "line 2"
                
            print("--- on: " + line)
            
            # Set pin in
            self.pinsIn[self.pinFlag] = True

            # stop flash
            if self.blinkTimer.isActive():
                self.blinkTimer.stop()
            
            # stop buzzer
            self.buzzer.quit()

            # turn this LED on
            self.pins[self.pinFlag-8].value = True

            # start incoming request
            self.incoming = OMXPlayer("/home/pi/apps/sb-pyqt/audio/1-Charlie_Operator.wav")

            # Send msg to screen
            self.label.setText("Connected to {}  \n".format(self.names[self.pinFlag]))

        else: # pin flag True, still, or again, high
            # was this a legit unplug?
            if (self.pinsIn[self.pinFlag]): # was plugged in
                # print("-- Pin {} has been disconnected \n".format(pin_flag-3))
                print("-- {} has been disconnected \n".format(self.names[self.pinFlag]))
                # debug message
                self.label.setText(" {} unplugged \n".format(self.names[self.pinFlag]))

                self.pinsIn[self.pinFlag] = False
            else:
                # self.label.setText("Illegitimate unplug from {}  \n".format(self.names[self.pinFlag]))

                print("got to pin true (changed to high), but not pin in")
        
        print("finished check \n")

        # self.mcp.clear_ints()
        self.just_checked = False


    def the_window_title_changed(self, window_title):
        print("window title changed so start bounceTimer: %s " % self.pinFlag)
        self.bounceTimer.start(1000)

    def mousePressEvent(self,e):
        self.label.setText("to be counted, & change title")
        # Audio
        # QSound.play("audio/buzzer.wav")
        # subprocess.call(['aplay -fdat /home/pi/apps/sb-pyqt/audio/buzzer.wav'], shell=True)
        self.buzzer = OMXPlayer("/home/pi/apps/sb-pyqt/audio/buzzer.wav")

        # block = False so sound will play asynchronously 
        # playsound("audio/buzzer.wav", block=False)
        self.blinkTimer.start(1000)

    def counter(self):
        self.count += 1
        # self.label.setText("count: " + str(self.count))
        self.pins[3].value = not self.pins[3].value
        # print("Count Stereo pin {} aledgedly now: {}".format(self.pinFlag, self.pins[self.pinFlag].value))


app = QApplication([])

win = MainWindow()
win.show()

sys.exit(app.exec_())
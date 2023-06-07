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
# from omxplayer.player import OMXPlayer
import vlc
import board
import busio
from digitalio import Direction, Pull
from RPi import GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017

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
        self.setGeometry(20,120,700,200)
        self.setCentralWidget(self.label)

        self.count = 0
        self.temp_window_count = 0
        self.blinking = True
        self.just_checked = False
        self.pinFlag = 15
        self.startBounceOnChange = False
        self.pinsIn = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]
        self.names = ["Mina","one","two","three","Freeman","five","Olive","seven","eight","nine","ten","eleven","twelve","thirteen"]
        self.blinkTimer=QTimer()
        self.blinkTimer.timeout.connect(self.counter)
        # self.buzzer = None
        self.buzzer = vlc.MediaPlayer("/home/pi/apps/sb-pyqt/audio/buzzer.wav")

        self.incoming = None
        self.outgoingTone = None
        self.convo = None
        self.whichLineInUse = -1
        self.whichLinePlugging = -1
        self.bounceTimer=QTimer()
        self.bounceTimer.timeout.connect(self.continueCheckPin)
        # Until I figure out a callback for when finished
        self.outgoingToneTimer=QTimer()
        self.outgoingToneTimer.timeout.connect(self.playConvo)

        self.windowTitleChanged.connect(self.the_window_title_changed)

        # Initialize the I2C bus:
        i2c = busio.I2C(board.SCL, board.SDA)
        self.mcp = MCP23017(i2c)
        self.mcpRing = MCP23017(i2c, address=0x22)

        # Make a list of all pins
        self.pins = []
        for pinIndex in range(0, 16):
            self.pins.append(self.mcp.get_pin(pinIndex))
        # # Set 0 - 7 to output
        # for pinIndex in range(0, 8):
        #     self.pins[pinIndex].switch_to_output(value=False)
        # Set 8 - 15 to input
        for pinIndex in range(0, 16):
            self.pins[pinIndex].direction = Direction.INPUT
            self.pins[pinIndex].pull = Pull.UP

        # Set up to check all the port B pins (pins 8-15) w/interrupts!
        self.mcp.interrupt_enable = 0xFFFF  # Enable Interrupts in all pins
        # self.mcp.interrupt_enable = 0xFF00  # Enable Interrupts in pins 8 - 15
        # self.mcp.interrupt_enable = 0b0001111100000000  # Enable Interrupts in pins 8 - 12 aka 0x1f00

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


        # -- Make a list of all RING pins --
        self.pinsRing = []
        for pinIndex in range(0, 12):
            self.pinsRing.append(self.mcpRing.get_pin(pinIndex))

        # # Set 0 - 7 to output
        # for pinIndex in range(0, 12):
        #     self.pinsRing[pinIndex].switch_to_output(value=False)


        # Set 0 - 15 to input
        for pinIndex in range(0, 12):
            self.pinsRing[pinIndex].direction = Direction.INPUT
            self.pinsRing[pinIndex].pull = Pull.UP


        def checkPin(port):
            """Callback function to be called when an Interrupt occurs."""
            for pin_flag in self.mcp.int_flag:
                # print("Interrupt connected to Pin: {}".format(port))
                # print("Interrupt pin_flag: {}".format(pin_flag))
                print("Interrupt - pin number: {} changed to: {} ".format(pin_flag,self.pins[pin_flag].value))
                
                if (not self.just_checked):
                    # print('checking bcz false')
                    self.just_checked = True
                    self.pinFlag = pin_flag
                    # trigger change that is detected to create an event in main thread
                    self.temp_window_count += 1
                    # new_window_title = choice(window_titles)
                    # print("setting title: %s" % new_window_title)
                    self.setWindowTitle("Window title: " + str(self.temp_window_count))

        GPIO.add_event_detect(interrupt, GPIO.BOTH, callback=checkPin, bouncetime=100)

    def continueCheckPin(self):
        # print('in continueCheckPin, pin_flag: ' + str(self.pinFlag))
        # print('in continueCheckPin, pin_flag value: ' + str(self.pins[self.pinFlag].value))
        self.bounceTimer.stop()

        print("In continue, pinFlag = " + str(self.pinFlag) + " val: " +
              str(self.pins[self.pinFlag].value))

        if (self.pins[self.pinFlag].value == False): # grounded by cable
            print("Pin {} is now connected".format(self.pinFlag))

            # line = "line 1"
            self.whichLinePlugging = 0

            print("Stereo (Ring) pin {} aledgedly now: {}".format(self.pinFlag, self.pinsRing[self.pinFlag].value))
            if (self.pinsRing[self.pinFlag].value == True):
                self.whichLinePlugging = 1
                
            print("--- on: " + str(self.whichLinePlugging))
            
            # Set pin in
            self.pinsIn[self.pinFlag] = True

            # stop flash
            if self.blinkTimer.isActive():
                self.blinkTimer.stop()
            
            # stop buzzer
            self.buzzer.stop()

            if self.pinFlag == 4:
                # track lines
                self.whichLineInUse = self.whichLinePlugging
                # start incoming request
                self.incoming = vlc.MediaPlayer("/home/pi/apps/sb-pyqt/audio/1-Charlie_Operator.wav")
                self.incoming.play()

                # # turn this LED on
                # self.pins[self.pinFlag-8].value = True

                # Send msg to screen
                self.label.setText("Hi.  72 please.")
                print("Connected to {}  \n".format(self.names[self.pinFlag]))
            elif self.pinFlag == 6:
                # stop incoming request
                print("Connected to {}  \n".format(self.names[self.pinFlag]))

                if self.whichLinePlugging == self.whichLineInUse:

                    # # turn this LED on
                    # self.pins[self.pinFlag-8].value = True

                    self.incoming.stop()
                    self.outgoingTone = vlc.MediaPlayer("/home/pi/apps/sb-pyqt/audio/outgoing-ring.wav")
                    self.outgoingTone.play()

                    # Until I figure out a callback for when finished
                    self.outgoingToneTimer.start(2000)
                    self.label.setText(
                        "Olive:  Hello? <br />" +
                        "Charlie:  Hi Olive, it’s Charlie.  Bowling's off. <br />" +
                        "Olive:  What's wrong? <br />" +
                        "Charlie:  My dad has a sick patient and he's taken the car. <br/>" +
                        "Olive:  I suppose that’s what it’s like when your dad’s a doctor. <br/>" +
                        "Charlie: Yeh.  He said I can’t hang out if he’s not here. <br/>" +
                        "Olive: That’s OK.  Maybe my mom can take us tomorrow. <br/>" +
                        "Charlie: That’d be cool.  But I gotta go.  Bye. <br/>" +
                        "Olive: Bye, bye."                
                    )
                else:
                    print("wrong line")

        else: # pin flag True, still, or again, high
            # was this a legit unplug?
            if (self.pinsIn[self.pinFlag]): # was plugged in
                # print("-- Pin {} has been disconnected \n".format(pin_flag-3))
                print("-- {} has been disconnected \n".format(self.names[self.pinFlag]))
                # debug message
                # self.label.setText(" {} unplugged \n".format(self.names[self.pinFlag]))

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
        self.label.setText("Keep your ears open for incoming calls")
        # Audio
        self.buzzer.play()
        self.blinkTimer.start(2000)

    def counter(self):
        self.count += 1

        # self.pinsRing[4].value = not self.pinsRing[4].value
        # print("count: " + str(self.count))

        # print("Count Stereo pin {} aledgedly now: {}".format(self.pinFlag, self.pins[self.pinFlag].value))

    def playConvo(self):
        self.outgoingTone.stop()
        self.outgoingToneTimer.stop()
        self.convo = vlc.MediaPlayer("/home/pi/apps/sb-pyqt/audio/2-Charlie_Calls_Olive.wav")
        self.convo.play()

app = QApplication([])

win = MainWindow()
win.show()

sys.exit(app.exec_())
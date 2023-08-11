import sys
import json
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

import vlc
import board
import busio
from digitalio import Direction, Pull
from RPi import GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017

from model import Model

contentJsonFile = open('conversations.json')
contentPy = json.load(contentJsonFile)

class MainWindow(qtw.QMainWindow): 
    # Almost all of this should be in separate module analogous to svelte Panel

    startPressed = qtc.pyqtSignal()
    plugEventDetected = qtc.pyqtSignal()
    plugInToHandle = qtc.pyqtSignal(dict)
    unPlugToHandle = qtc.pyqtSignal(int)
    wiggleDetected = qtc.pyqtSignal()

    def __init__(self):
        # self.pygame.init()
        super().__init__()

        # ------- pyqt window ----
        self.setWindowTitle("You Are the Operator")
        self.label = qtw.QLabel(self)
        self.label.setWordWrap(True)
        self.label.setText("Keep your ears open for incoming calls! ")
        self.label.setAlignment(qtc.Qt.AlignTop)
        # self.label.setStyleSheet("vertical-align: top;")
        self.setGeometry(20,120,600,200)
        self.setCentralWidget(self.label)

        self.model = Model()

        self.count = 0
        # self.temp_window_count = 0
        # self.blinking = True
        self.just_checked = False
        self.pinFlag = 15
        self.startBounceOnChange = False
        self.pinsIn = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]
        self.names = ["Mina","one","two","three","Freeman","five","Olive","seven","eight","nine","ten","eleven","twelve","thirteen"]

        # ------ phone call logic------
        self.incoming = None
        self.outgoingTone = None
        self.convo = None
        self.whichLineInUse = -1
        self.whichLinePlugging = -1

        # --- timers --- 
        self.bounceTimer=qtc.QTimer()
        self.bounceTimer.timeout.connect(self.continueCheckPin)
        self.blinkTimer=qtc.QTimer()
        self.blinkTimer.timeout.connect(self.blinker)
        # Supress interrupt when plug is just wiggled
        self.wiggleDetected.connect(lambda: self.wiggleTimer.start(1000))
        self.wiggleTimer=qtc.QTimer()
        self.wiggleTimer.timeout.connect(self.checkWiggle)

        # Until I figure out a callback for when finished
        self.outgoingToneTimer=qtc.QTimer()
        self.outgoingToneTimer.timeout.connect(self.playConvo)


        # Experiment with changed.connect
        # self.startUpTimer=QTimer()
        # self.startUpTimer.timeout.connect(self.continueCheckPin)  
           
        # Self (control) for gpio related, self.model for audio
        # Okay to connect to both
        self.startPressed.connect(self.handleStart)
        self.startPressed.connect(self.model.handleStart)

        self.plugEventDetected.connect(lambda: self.bounceTimer.start(1000))
        self.plugInToHandle.connect(self.model.handlePlugIn)
        self.unPlugToHandle.connect(self.model.handleUnPlug)

        self.model.displayText.connect(self.setScreenLabel)

        # Initialize the I2C bus:
        i2c = busio.I2C(board.SCL, board.SDA)
        self.mcp = MCP23017(i2c) # default address-0x20
        self.mcpRing = MCP23017(i2c, address=0x22)
        self.mcpLed = MCP23017(i2c, address=0x21)

        # -- Make a list of pins for each bonnet, set input/output --
        # Plug tip, which will trigger interrupts
        self.pins = []
        for pinIndex in range(0, 16):
            self.pins.append(self.mcp.get_pin(pinIndex))
        # Set to input - later will get intrrupt as well
        for pinIndex in range(0, 16):
            self.pins[pinIndex].direction = Direction.INPUT
            self.pins[pinIndex].pull = Pull.UP

        # Stereo "ring" which will detect 1st vs 2nd line
        self.pinsRing = []
        for pinIndex in range(0, 12):
            self.pinsRing.append(self.mcpRing.get_pin(pinIndex))
        # Set to input
        for pinIndex in range(0, 12):
            self.pinsRing[pinIndex].direction = Direction.INPUT
            self.pinsRing[pinIndex].pull = Pull.UP

        # pinsLed are in model.py
        # LEDs 
        # Tried to put these in the Model/logic module -- but seems all gpio
        # needs to be in this base/main module
        self.pinsLed = []
        for pinIndex in range(0, 12):
            self.pinsLed.append(self.mcpLed.get_pin(pinIndex))
        # Set to output
        for pinIndex in range(0, 12):
           self.pinsLed[pinIndex].switch_to_output(value=False)

        # -- Set up Tip interrupt --
        self.mcp.interrupt_enable = 0xFFFF  # Enable Interrupts in all pins
        # self.mcp.interrupt_enable = 0xFFF  # Enable Interrupts first 12 pins
        # self.mcp.interrupt_enable = 0b0000111111111111  # Enable Interrupts in pins 0-11 aka 0xfff

        # If intcon is set to 0's we will get interrupts on both
        #  button presses and button releases
        self.mcp.interrupt_configuration = 0x0000  # interrupt on any change
        self.mcp.io_control = 0x44  # Interrupt as open drain and mirrored
        # put this in startup?
        self.mcp.clear_ints()  # Interrupts need to be cleared initially

        # connect either interrupt pin to the Raspberry pi's pin 17.
        # They were previously configured as mirrored.
        GPIO.setmode(GPIO.BCM)
        interrupt = 17
        GPIO.setup(interrupt, GPIO.IN, GPIO.PUD_UP)  # Set up Pi's pin as input, pull up

        # -- code for detection --
        def checkPin(port):
            """Callback function to be called when an Interrupt occurs.
            The signal for pluginEventDetected calls a timer -- it can't send
            a parameter, so the work-around is to set pin_flag as a global.
            """
            for pin_flag in self.mcp.int_flag:
                # print("Interrupt connected to Pin: {}".format(port))
                print(f"Interrupt - pin number: {pin_flag} changed to: {self.pins[pin_flag].value}")

                # Test for phone jack vs start and stop buttons
                if (pin_flag < 12):

                    if (not self.just_checked):
                        # print('checking bcz false')
                        self.pinFlag = pin_flag

                        # If this pin is in, delay before checking
                        if (self.pinsIn[pin_flag]):
                            print(f"pin {pin_flag} is already in")
                            # To be done: prevent re-check if pin remains in
                            # after a wiggle
                            # self.wiggleTimer.start(1000)
                            self.wiggleDetected.emit()

                        else: # pin is not in, new event
                            # do standard check
                            self.just_checked = True
                            # self.pinFlag = pin_flag
                            # self.plugEventDetected.emit(f"idxInfo:  {pin_flag}")
                            # The following signal starts a timer that will continue
                            # the check. This provides bounce protection
                            # This signal is separate from the main python event loop
                            self.plugEventDetected.emit()

                else:
                    print("got to interupt 12 or greater")
                    self.startPressed.emit()
                    # if (pin_flag == 12):
                    # self.pinsLed[0].value = True

        GPIO.add_event_detect(interrupt, GPIO.BOTH, callback=checkPin, bouncetime=100)

    def continueCheckPin(self):
        # Not able to send param through timer, so pinFlag has been set globaly
        # print("In continue, pinFlag = " + str(self.pinFlag) + " val: " +
        #       str(self.pins[self.pinFlag].value))

        self.bounceTimer.stop()

        if (self.pins[self.pinFlag].value == False): # grounded by cable
            """False/grouded, then this event is a plug-in
            """
            print(f"Pin {self.pinFlag} is now connected")

            # Determine which line
            self.whichLinePlugging = 0
            print("Stereo (Ring) pin {} aledgedly now: {}".format(self.pinFlag, self.pinsRing[self.pinFlag].value))
            if (self.pinsRing[self.pinFlag].value == True):
                self.whichLinePlugging = 1
            print("--- on: " + str(self.whichLinePlugging))

            # Send plugin info to model.py
            # Send key value object or duple, or array w two ints
            # self.plugInToHandle.emit(f"plugin - pin: {self.pinFlag}, line: {self.whichLinePlugging}")
            self.plugInToHandle.emit({"personIdx": self.pinFlag, "lineIdx": self.whichLinePlugging})

            # Set pin in
            self.pinsIn[self.pinFlag] = True

            # # stop flashing if on
            if self.blinkTimer.isActive():
                self.blinkTimer.stop()
            # # stop buzzer handled in model
            # self.buzzer.stop()

            if self.pinFlag == 4:
                """ Wow, lot's to do here
                Can I keep splitting gpio here with logic in model?
                Could signal from model to a slot here which does things
                like turn the LED on
                """
                # track lines
                self.whichLineInUse = self.whichLinePlugging
                # start incoming request
                self.incoming = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
                self.incoming.play()

                # # turn this LED on
                self.pinsLed[self.pinFlag].value = True

                # Send msg to screen
                # self.label.setText("Hi.  72 please.")
                # self.label.setText(content.charlieHello())
                self.label.setText(contentPy[0]["helloText"])

                print("Connected to {}  \n".format(self.names[self.pinFlag]))

            elif self.pinFlag == 6:
                # stop incoming request
                print("Connected to {}  \n".format(self.names[self.pinFlag]))

                if self.whichLinePlugging == self.whichLineInUse:

                    # # turn this LED on
                    self.pinsLed[self.pinFlag].value = True

                    self.incoming.stop()
                    self.outgoingTone = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/outgoing-ring.mp3")
                    self.outgoingTone.play()

                    # Until I figure out a callback for when finished
                    self.outgoingToneTimer.start(1000)

                    self.label.setText(contentPy[0]["convoText"])

                else:
                    print("wrong line")

        else: # pin flag True, still, or again, high
            # On unplug we can't tell which line electonicaly 
            # (diff in shaft is gone), so rely on pinsIn info
            # self.unPlugToHandle.emit(f"unplug - pin: {self.pinFlag}")
            self.unPlugToHandle.emit(self.pinFlag)

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
        
        # print("finished check \n")

        # self.mcp.clear_ints()
        # self.just_checked = False
        # Delay setting just_check to false in case the plug is wiggled
        qtc.QTimer.singleShot(2000, self.delayedFinishCheck)

    def delayedFinishCheck(self):
        print("delayed finished check \n")
        self.just_checked = False

    def checkWiggle(self):
        print("got to checkWiggle")
        self.wiggleTimer.stop()
        # Check whether the pin still grounded
        # if no longer grounded, proceed with event detection
        if (not self.pins[self.pinFlag].value == False):
            # The pin is no longer in
            self.just_checked = True
            self.plugEventDetected.emit()
        # else:
            # if still grounded 
            # do nothing
            # pin has been removed during pause

    def handleStart(self):
        """Just for startup
        self.model.handleStart is called simultaneously -- for text
        """
        print("start up")
        # self.model.handleStart handles sound
        self.blinkTimer.start(600)
        self.pinsLed[4].value = not self.pinsLed[4].value

    def blinker(self):
        # print("blinking")
        self.pinsLed[4].value = not self.pinsLed[4].value
        
    def playConvo(self):
        self.outgoingTone.stop()
        self.outgoingToneTimer.stop()
        self.convo = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/2-Charlie_Calls_Olive.mp3")
        self.convo.play()

    def setScreenLabel(self, msg):
        self.label.setText(msg)        

app = qtw.QApplication([])

win = MainWindow()
win.show()

sys.exit(app.exec_())
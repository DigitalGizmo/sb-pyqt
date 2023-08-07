import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

import board
import busio
from digitalio import Direction, Pull
from RPi import GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017

# class StartupSender(QObject):
#     startPressed = pyqtSignal()

class Panel(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)
    startPressed = qtc.pyqtSignal()
    pinChanged = qtc.pyqtSignal(str)

    pinTest = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        # ------ PyQt Section -------
        self.setLayout(qtw.QVBoxLayout())
        self.otherbutton = qtw.QPushButton('Other', clicked=self.onOther)
        self.layout().addWidget(self.otherbutton)

        # ------- Constants -------
        self.just_checked = False
        self.pinFlag = 15
        self.startBounceOnChange = False
        self.pinsIn = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]

        # -- signal connections
        # self.startUpObject = StartupSender()
        # self.startPressed.connect(self.startFirstCall)
        self.startPressed.connect(self.onStart)
        
        
        self.pinTest.connect(self.pinChangeDetected)


        # self.pinChanged.connect(self.pinChangeDetected) # pinChangeDetected starts timer
        # self.pinChanged.connect(self.continueCheckPin)
        # self.pinTest.connect(self.continueCheckPin)

        self.bounceTimer=qtc.QTimer()
        self.bounceTimer.timeout.connect(self.continueCheckPin)


        # Initialize the I2C bus:
        i2c = busio.I2C(board.SCL, board.SDA)
        self.mcp = MCP23017(i2c) # default address-0x20
        self.mcpRing = MCP23017(i2c, address=0x22)
        self.mcpLed = MCP23017(i2c, address=0x21)


        # --------- GPIO Section -------
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

        # Stereo "ring" which will detect 1st vs 2nd line
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
            """Callback function to be called when an Interrupt occurs."""
            for pin_flag in self.mcp.int_flag:
                # print("Interrupt connected to Pin: {}".format(port))
                # print("Interrupt pin_flag: {}".format(pin_flag))
                # print(f"Interrupt - pin number: {pin_flag} changed to: {self.pins[pin_flag].value} ")

                # New for start button
                if (pin_flag < 12):
                    # As-ws
                    print(f"about to check pin. just_checked is: {self.just_checked}")
                    if (not self.just_checked):
                        # print('checking bcz false')
                        self.just_checked = True
                        self.pinFlag = pin_flag

                        # print(f"Got to jack: {pin_flag}")


                        # self.pinChanged.emit(f"pin_flag: {pin_flag} detected")

                        self.pinTest.emit()


                        # self.setWindowTitle("Window title: " + str(self.temp_window_count))
                        
                        
                        # will trigger continuCheckPin
                        # Work-around for action loop
                else:
                    print("got to interupt 12 or greater")
                    self.startPressed.emit()
                    # if (pin_flag == 12):
                    #     # self.setGeometry(20,120,600,190)
                    #     self.label.setWordWrap(False)


        GPIO.add_event_detect(interrupt, GPIO.BOTH, callback=checkPin, bouncetime=100)


    def onOther(self):
        self.submitted.emit('I did this')
        # self.close()

    def onStart(self):
        self.submitted.emit('We can start now')

    # def pinChangeDetected(self, msg):
    def pinChangeDetected(self):
        # self.submitted.emit('We can start now')
        # print(f"pinChangeDetected, pin: {msg}")
        print(f"pinChangeDetected, start bounceTimer")
        self.bounceTimer.start(1000)

    # def continueCheckPin(self, msg):
    def continueCheckPin(self):
        self.bounceTimer.stop()
        # print(f"got to continueCheckPin. just_checked = {self.just_checked}")
        self.submitted.emit('this is from continueCheckPin')
        self.just_checked = False
        print(f"in continueCheckPin. Should be false - just_checked = {self.just_checked}")

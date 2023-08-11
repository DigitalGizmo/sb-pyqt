import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import vlc

class Model(qtc.QObject):
    """Main logic patterned after software proto
    """
    displayText = qtc.pyqtSignal(str)
    # self.buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")
    # buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")

    def __init__(self):
        super().__init__()

        # The following possibly in veiw
        self.buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")

        self.whichLineInUse = -1

        self.phoneLines = [
            {
                "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
            },
            {
                "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
            }
        ]


    def handlePlugIn(self, pluggedIdxInfo):
        """triggered by control.py
        """
        print(f'handlePlugIn, pin: {pluggedIdxInfo["personIdx"]}, line: {pluggedIdxInfo["lineIdx"]}')
        # Blinker handdles in control.py
        self.buzzer.stop()

        if pluggedIdxInfo["personIdx"] == 4:
            """ Wow, lot's to do here
            """
            # track lines
            self.whichLineInUse = pluggedIdxInfo["lineIdx"]
            # start incoming request

            self.playHello(0, self.whichLineInUse)
            # self.incoming = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
            # self.incoming.play()

            # # turn this LED on
            # self.pinsLed[self.pinFlag].value = True

            # Send msg to screen
            # self.label.setText("Hi.  72 please.")
            # self.label.setText(content.charlieHello())


            # self.label.setText(contentPy[0]["helloText"])
            self.displayText.emit("Temp Charlie saying hello")


            # print("Connected to {}  \n".format(self.names[self.pinFlag]))
            print(f"In Model: Connected to {pluggedIdxInfo['personIdx']}")




    def handleUnPlug(self, pinIndex):
        """ triggered by control.py
        """
        print(f"handle unPlug: {pinIndex}")


    def handleStart(self):
        """Just for startup
        """
        print("start up")

        self.buzzer.play()
        # self.blinkTimer.start(1000)
        # self.pinsLed[4].value = not self.pinsLed[4].value
        # self.pinsLed[4].value = True

        self.displayText.emit("Start text for screen-- Incoming")

    def playHello(self, _currConvo, lineIndex):
        self.phoneLines[lineIndex] = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
        self.phoneLines[lineIndex].play()
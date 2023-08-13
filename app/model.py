# import sys
import json
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import vlc

contentJsonFile = open('conversations.json')
contentPy = json.load(contentJsonFile)

class Model(qtc.QObject):
    """Main logic patterned after software proto
    """
    displayText = qtc.pyqtSignal(str)
    ledEvent = qtc.pyqtSignal(int, bool)
    blinkerStart = qtc.pyqtSignal(int)
    blinkerStop = qtc.pyqtSignal()
    # self.buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")
    # buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")

    def __init__(self):
        super().__init__()

        # The following possibly in veiw
        self.buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")
        self.outgoingTone = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/outgoing-ring.mp3")
        # Until I figure out a callback for when finished
        self.outgoingToneTimer=qtc.QTimer()
        self.outgoingToneTimer.timeout.connect(self.playConvo)

        self.whichLineInUse = -1

        self.phoneLines = [
            {
                "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
            },
            {
                "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
            }
        ]


    # def handlePlugIn(self, pluggedIdxInfo):
    def handlePlugIn(self, pluggedIdxInfo):
        personIdx = pluggedIdxInfo['personIdx']
        lineIdx = pluggedIdxInfo['lineIdx']
        """triggered by control.py
        """
        print(f'handlePlugIn, pin: {personIdx}, line: {lineIdx}')
        # Blinker handdled in control.py
        self.buzzer.stop()
        self.blinkerStop.emit()

        if personIdx == 4:
            """ Wow, lot's to do here
            """
            # track lines
            self.whichLineInUse = lineIdx
            # start incoming request
            self.playHello(0, self.whichLineInUse)
            # # turn this LED on
            self.ledEvent.emit(personIdx, True)
            # Send msg to screen
            self.displayText.emit(contentPy[0]["helloText"])
            # print("Connected to {}  \n".format(self.names[self.pinFlag]))
            print(f"In Model: Connected to {pluggedIdxInfo['personIdx']}")

        elif personIdx == 6:
            # stop incoming request
            print(f"In Model: Connected to {pluggedIdxInfo['personIdx']}")

            if (self.whichLineInUse == lineIdx):

                # # turn this LED on
                self.ledEvent.emit(personIdx, True)

                # self.incoming.stop()
                # self.handlePlugInphoneLines[pluggedIdxInfo["lineIdx"]].audioTrack.volume = 0;
                self.phoneLines[lineIdx].stop()

                # self.outgoingTone = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/outgoing-ring.mp3")
                self.outgoingTone.play()

                # Until I figure out a callback for when finished
                self.outgoingToneTimer.start(1000)


                # self.label.setText(contentPy[0]["convoText"])
                self.displayText.emit(contentPy[0]["convoText"])

            else:
                print("wrong line")



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

        self.blinkerStart.emit(3)

        self.displayText.emit("Start text for screen-- Incoming")

    def playHello(self, _currConvo, lineIndex):
        self.phoneLines[lineIndex] = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
        self.phoneLines[lineIndex].play()

    def playConvo(self):
        self.outgoingTone.stop()
        self.outgoingToneTimer.stop()
        self.convo = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/2-Charlie_Calls_Olive.mp3")
        self.convo.play()

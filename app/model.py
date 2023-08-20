# import sys
import json
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import vlc

conversationsJsonFile = open('conversations.json')
conversations = json.load(conversationsJsonFile)
personsJsonFile = open('persons.json')
persons = json.load(personsJsonFile)

class Model(qtc.QObject):
    """Main logic patterned after software proto
    """
    displayText = qtc.pyqtSignal(str)
    ledEvent = qtc.pyqtSignal(int, bool)
    # pinInEvent = qtc.pyqtSignal(int, bool)
    blinkerStart = qtc.pyqtSignal(int)
    blinkerStop = qtc.pyqtSignal()
    # self.buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")
    # buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")
    # Put pinsIn here in model where it's used more often
    # rather than in control which would require a lot of signaling.
    pinsIn = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]

    def __init__(self):
        super().__init__()

        # pinsIn = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]

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

    def setPinsIn(self, pinIdx, pinVal):
        self.pinsIn[pinIdx] = pinVal

    def getPinsIn(self, pinIdx):
        return self.pinsIn[pinIdx]

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

            # Set pinsIn True
            # self.pinInEvent.emit(personIdx, True)

            self.setPinsIn(personIdx, True)


            # Send msg to screen
            self.displayText.emit(conversations[0]["helloText"])
            # print("Connected to {}  \n".format(self.names[self.pinFlag]))
            print(f"In Model: Connected to {pluggedIdxInfo['personIdx']}")

        elif personIdx == 6:
            # stop incoming request
            print(f"In Model: Connected to {pluggedIdxInfo['personIdx']}")

            if (self.whichLineInUse == lineIdx):
                # # turn this LED on
                self.ledEvent.emit(personIdx, True)

                # Set pinsIn True
                # self.pinInEvent.emit(personIdx, True)
                self.setPinsIn(personIdx, True)

                self.phoneLines[lineIdx].stop()
                self.outgoingTone.play()

                # Until I figure out a callback for when finished
                self.outgoingToneTimer.start(1000)

                self.displayText.emit(conversations[0]["convoText"])

            else:
                print("wrong line")

    def handleUnPlug(self, personIdx):
        """ triggered by control.py
        """
        print(f"handle unPlug: {personIdx}")
        # Set pinIn False
        # self.pinInEvent.emit(personIdx, False)
        self.setPinsIn(personIdx, False)

    def handleStart(self):
        """Just for startup
        """
        # print("start up")
        self.buzzer.play()
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

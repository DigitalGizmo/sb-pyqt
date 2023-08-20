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
    # buzzer = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")
    buzzTrack = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")
    outgoingTone = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/outgoing-ring.mp3")
    # Put pinsIn here in model where it's used more often
    # rather than in control which would require a lot of signaling.
    pinsIn = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]
    # # Until I figure out a callback for when finished
    # outgoingToneTimer=qtc.QTimer()
    # outgoingToneTimer.timeout.connect(self.playConvo)


    currConvo = 0
    currCallerIndex = 0
    currCalleeIndex = 0
    whichLineInUse = -1
    prevLineInUse = -1

    callInitTimer = qtc.QTimer()
    # reconnectTimer = undefined
    audioCaption = " "

    LED_OFF = 0
    LED_BLINKING = 1
    LED_SOLID = 2

    NO_UNPLUG_STATUS = 0
    AWAITING_INTERRUPT = 1
    DURING_INTERRUPT_SILENCE = 2
    REPLUG_IN_PROGRESS = 3
    CALLER_UNPLUGGED = 5




    phoneLines = [
        {
			"isEngaged": False,
			"unPlugStatus": NO_UNPLUG_STATUS,
			"caller": {"index": 99, "isPlugged": False},
			"callee": {"index": 99, "isPlugged": False},
            # "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
        },
        {
			"isEngaged": False,
			"unPlugStatus": NO_UNPLUG_STATUS,
			"caller": {"index": 99, "isPlugged": False},
			"callee": {"index": 99, "isPlugged": False},
            # "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
        }
    ]


    outgoingToneTimer=qtc.QTimer()
    # outgoingToneTimer.timeout.connect(playConvo)


    def __init__(self):
        super().__init__()
        # # Until I figure out a callback for when finished
        # self.outgoingToneTimer=qtc.QTimer()
        self.outgoingToneTimer.timeout.connect(self.playConvo)

    def setPinsIn(self, pinIdx, pinVal):
        self.pinsIn[pinIdx] = pinVal

    def getPinsIn(self, pinIdx):
        return self.pinsIn[pinIdx]


    def initiateCall(self):
        if (self.currConvo < 9):
            currCallerIndex =  conversations[self.currConvo]["caller"]["index"]
            # Set "target", person being called
            currCalleeIndex = conversations[self.currConvo]["callee"]["index"]
            # This just rings the buzzer. Next action will
            # be when user plugs in a plug - in Panel.svelte drag end: handlePlugIn
            self.buzzTrack.play()
            # buzzTrack.volume = .6    

            # persons[conversations[self.currConvo]["caller"]["index"]]["ledState"] = self.LED_BLINKING

            # self.blinkerStart.emit(3)
            self.blinkerStart.emit(conversations[self.currConvo]["caller"]["index"])

            self.displayText.emit("Start text for screen-- Incoming")\
            
            print('-- New call being initiated by: ' + 
                persons[conversations[self.currConvo]["caller"]["index"]]["name"])
        else:
            # Play congratulations
            print("Congratulations - done!")
            # self.phoneLines[0].audioTrack =
            #     new Audio("https://dev.digitalgizmo.com/msm-ed/ed-assets/audio/FinishedActivity.mp3")
            #     phoneLines[0].audioTrack.play()



    # def handlePlugIn(self, pluggedIdxInfo):
    def handlePlugIn(self, pluggedIdxInfo):
        """triggered by control.py
        """
        personIdx = pluggedIdxInfo['personIdx']
        lineIdx = pluggedIdxInfo['lineIdx']
        # print(f'handlePlugIn, pin: {personIdx}, line: {lineIdx}')


        # Blinker handdled in control.py
        self.buzzTrack.stop()
        self.blinkerStop.emit()

        # if (not self.phoneLines[lineIdx]["caller"]["isPlugged"]):
        #     print(f"--- this line, not plugged")

		# ********
		# Fresh plug-in -- aka caller not plugged
		#*******/
		# Is this new use of line -- caller has not been plugged in.

        # if (not self.phoneLines[lineIdx]["caller"]["isPlugged"]):


        if personIdx == 4:
        # if (not self.phoneLines[lineIdx].caller.isPlugged): 
            """ Wow, lot's to do here
            """
            # track lines
            self.whichLineInUse = lineIdx
            # start incoming request
            self.playHello(0, self.whichLineInUse)
            # # turn this LED on
            self.ledEvent.emit(personIdx, True)
            # Set pinsIn True
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
                self.setPinsIn(personIdx, True)
                self.phoneLines[lineIdx].stop()
                self.outgoingTone.play()

                # Until I figure out a callback for when finished
                self.outgoingToneTimer.start(1000)

                self.displayText.emit(conversations[0]["convoText"])

            else:
                print("wrong line")

        # else: # caller is plugged
			#********
		    # Other end of the line -- caller is plugged, so this must be the other plug
			#********/
			# But first, make sure this is the line in use
            print(f"Which line in use: {lineIdx}")
            # if (lineIdx == self.whichLineInUse):
			# 	# Whether or not this is correct callee -- turn LED on.
            #     # # turn this LED on
            #     self.ledEvent.emit(personIdx, True)
            #     # Set pinsIn True
            #     self.setPinsIn(personIdx, True)
            #     self.phoneLines[lineIdx].stop()
            #     self.outgoingTone.play()

            #     # Until I figure out a callback for when finished
            #     self.outgoingToneTimer.start(1000)

            #     self.displayText.emit(conversations[0]["convoText"])

        

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
        self.initiateCall()
        # # print("start up")
        # self.buzzer.play()
        # self.blinkerStart.emit(3)
        # self.displayText.emit("Start text for screen-- Incoming")

    def playHello(self, _currConvo, lineIndex):
        self.phoneLines[lineIndex] = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
        self.phoneLines[lineIndex].play()

    # def playConvo(self):
    def playConvo(self):
        self.outgoingTone.stop()
        self.outgoingToneTimer.stop()
        self.convo = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/2-Charlie_Calls_Olive.mp3")
        self.convo.play()

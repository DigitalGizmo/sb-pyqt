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

    toneInstace = vlc.Instance()
    tonePlayer = toneInstace.media_player_new()
    toneEvents = tonePlayer.event_manager()

    vlcInstances = [vlc.Instance(), vlc.Instance()]
    vlcPlayers = [vlcInstances[0].media_player_new(), vlcInstances[1].media_player_new()]
    vlcEvents = [vlcPlayers[0].event_manager(), vlcPlayers[1].event_manager()]

    buzzTrack = vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/buzzer.mp3")

    def __init__(self):
        super().__init__()
        self.callInitTimer = qtc.QTimer()
        self.callInitTimer.setSingleShot(True)
        self.callInitTimer.timeout.connect(self.initiateCall)
        # reconnectTimer = undefined
        # audioCaption = " "
        self.reset()

    def reset(self):
        self.stopAllAudio()

        # Put pinsIn here in model where it's used more often
        # rather than in control which would require a lot of signaling.
        self.pinsIn = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]
        self.currConvo = 1
        self.currCallerIndex = 0
        self.currCalleeIndex = 0
        self.whichLineInUse = -1
        self.prevLineInUse = -1


        self.NO_UNPLUG_STATUS = 0
        self.AWAITING_INTERRUPT = 1
        self.DURING_INTERRUPT_SILENCE = 2
        self.REPLUG_IN_PROGRESS = 3
        self.CALLER_UNPLUGGED = 5

        self.phoneLines = [
            {
                "isEngaged": False,
                "unPlugStatus": self.NO_UNPLUG_STATUS,
                "caller": {"index": 99, "isPlugged": False},
                "callee": {"index": 99, "isPlugged": False},
                "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
            },
            {
                "isEngaged": False,
                "unPlugStatus": self.NO_UNPLUG_STATUS,
                "caller": {"index": 99, "isPlugged": False},
                "callee": {"index": 99, "isPlugged": False},
                "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
            }
        ]

    def stopAllAudio(self):
        if self.callInitTimer.isActive():
            self.callInitTimer.stop()

        self.vlcPlayers[0].stop()
        self.vlcPlayers[1].stop()
        self.tonePlayer.stop()


    def setPinsIn(self, pinIdx, pinVal):
        self.pinsIn[pinIdx] = pinVal

    def getPinsIn(self, pinIdx):
        return self.pinsIn[pinIdx]


    def initiateCall(self):
        if (self.currConvo < 9):
            self.currCallerIndex =  conversations[self.currConvo]["caller"]["index"]
            # Set "target", person being called
            self.currCalleeIndex = conversations[self.currConvo]["callee"]["index"]
            # This just rings the buzzer. Next action will
            # be when user plugs in a plug - in Panel.svelte drag end: handlePlugIn
            self.buzzTrack.play()
            # buzzTrack.volume = .6    

            # self.blinkerStart.emit(3)
            self.blinkerStart.emit(conversations[self.currConvo]["caller"]["index"])

            self.displayText.emit("Start text for screen-- Incoming")
            
            print('-- New call being initiated by: ' + 
                persons[conversations[self.currConvo]["caller"]["index"]]["name"])
        else:
            # Play congratulations
            print("Congratulations - done!")
            # self.phoneLines[0].audioTrack =
            #     new Audio("https://dev.digitalgizmo.com/msm-ed/ed-assets/audio/FinishedActivity.mp3")
            #     phoneLines[0].audioTrack.play()

    def playHello(self, _currConvo, lineIndex):
        media = self.vlcInstances[lineIndex].media_new_path("/home/piswitch/Apps/sb-audio/" + 
            conversations[_currConvo]["helloFile"] + ".mp3")
        self.vlcPlayers[lineIndex].set_media(media)
        self.vlcPlayers[lineIndex].play()

        # Send msg to screen
        self.displayText.emit(conversations[self.currConvo]["helloText"])


    def playConvo(self, currConvo, lineIndex):
        """
        This just plays the outgoing tone and then starts the full convo
        """

        # Long VLC way of creating callback
        self.toneEvents.event_attach(vlc.EventType.MediaPlayerEndReached, 
            self.playFullConvo, currConvo, lineIndex) # playFullConvo(currConvo, lineIndex)
        

        media = self.toneInstace.media_new_path("/home/piswitch/Apps/sb-audio/outgoing-ring.mp3")
        self.tonePlayer.set_media(media)
        self.tonePlayer.play()

    def playFullConvo(self, event, _currConvo, lineIndex):
        """
        In software proto playConvo was just the tone. It had a callback
        Wish I could pass parameters, but this is called by timer
        currConvo is already a global, lineArgForConvo is a global created for this purpose
        """
        # print(f"fullconvo, convo: {_currConvo}, linedx: {lineIndex}, dummy: {dummy}")


        # self.outgoingTone.stop()
        # self.outgoingToneTimer.stop()
        self.displayText.emit(conversations[_currConvo]["convoText"])

        # Simulate callback for convo track finish
        self.vlcEvents[lineIndex].event_attach(vlc.EventType.MediaPlayerEndReached, 
            self.setCallCompleted, _currConvo, lineIndex)

        media = self.vlcInstances[lineIndex].media_new_path("/home/piswitch/Apps/sb-audio/" + 
            conversations[_currConvo]["convoFile"] + ".mp3")

        self.vlcPlayers[lineIndex].set_media(media)
        self.vlcPlayers[lineIndex].play()


    def setCallCompleted(self, event, _currConvo, lineIndex): #, _currConvo, lineIndex
        print("conversation finished")
        print(f"fullconvo, convo: {_currConvo}, linedx: {lineIndex}")


    # def handlePlugIn(self, pluggedIdxInfo):
    def handlePlugIn(self, pluggedIdxInfo):
        """triggered by control.py
        """
        personIdx = pluggedIdxInfo['personIdx']
        lineIdx = pluggedIdxInfo['lineIdx']
        # print(f'handlePlugIn, pin: {personIdx}, line: {lineIdx}')

		# ********
		# Fresh plug-in -- aka caller not plugged
		# *******/
		# Is this new use of line -- caller has not been plugged in.
        if (not self.phoneLines[lineIdx]["caller"]["isPlugged"]):
            # Did user plug into caller?
            # if personIdx == 4:
            if personIdx == self.currCallerIndex:
            # if (not self.phoneLines[lineIdx].caller.isPlugged): 
                """ Wow, lot's to do here
                """
                # # turn this LED on
                self.ledEvent.emit(personIdx, True)

                # Set this person's jack to plugged
				# persons[personIdx].isPluggedJack = true;
                self.setPinsIn(personIdx, True)

                # Set this line as having caller plugged
                self.phoneLines[lineIdx]["caller"]["isPlugged"] = True
                # Set identity of caller on this line
                self.phoneLines[lineIdx]["caller"]["index"] = personIdx;				
                # Set this line in use only we have gotten this success
                self.whichLineInUse = lineIdx

                # Blinker handdled in control.py
                print("stopping buzz track?")
                self.buzzTrack.stop()
                self.blinkerStop.emit()

                # start incoming request
                self.playHello(0, self.whichLineInUse)

                # # Send msg to screen
                # self.displayText.emit(conversations[0]["helloText"])
                # print("Connected to {}  \n".format(self.names[self.pinFlag]))
                print(f"In Model: Connected to {pluggedIdxInfo['personIdx']}")

                #  Handle case where caller was unplugged
                # if...






        else: # caller is plugged
			#********
		    # Other end of the line -- caller is plugged, so this must be the other plug
			#********/
			# But first, make sure this is the line in use
            # print(f"Which line in use: {lineIdx}")
            if (lineIdx == self.whichLineInUse):
				# Whether or not this is correct callee -- turn LED on.
                # # turn this LED on
                self.ledEvent.emit(personIdx, True)
                # Set pinsIn True
                self.setPinsIn(personIdx, True)
				# Stop the hello operator track
                # self.phoneLines[lineIdx]["audioTrack"].stop()

                # Silence incoming Hello/Request, whether this is the correct
                # callee or not
                self.vlcPlayers[lineIdx].stop()


                # Set callee -- used by unPlug even if it's the wrong number
                self.phoneLines[lineIdx]["callee"]["index"] = personIdx

                if (personIdx == self.currCalleeIndex): # Correct callee
                    print(f"plugged into correct callee, idx: {personIdx}")
                    # Set this line as engaged
                    self.phoneLines[lineIdx]["isEngaged"] = True
                    # Also set line callee plugged
                    self.phoneLines[lineIdx]["callee"]["isPlugged"] = True
                    # # Silence incoming Hello/Request, if necessary
                    # self.vlcPlayers[lineIdx].stop()

                    self.playConvo(self.currConvo,	lineIdx)

                else:
                    print("wrong line")
        

    def handleUnPlug(self, personIdx):
        """ triggered by control.py
        """
        print(f"handle unPlug: {personIdx}")
        # Set pinIn False
        # self.pinInEvent.emit(personIdx, False)
        self.setPinsIn(personIdx, False)
        print(f"pin {personIdx} is now {self.pinsIn[personIdx]}")

    def handleStart(self):
        """Just for startup
        """
        hasPinsIn = False
        for pinVal in self.pinsIn:
            if pinVal == True:
                hasPinsIn = True

        if hasPinsIn:
            self.stopAllAudio()
            self.displayText.emit("pins still in, remove and press Start again")
            # print("pins still in, remove and press Start again")

        else:
            self.reset()
            # self.initiateCall()
            self.callInitTimer.start(2000)


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
    # The following signals are connected in control.py
    displayText = qtc.pyqtSignal(str)
    ledEvent = qtc.pyqtSignal(int, bool)
    # pinInEvent = qtc.pyqtSignal(int, bool)
    blinkerStart = qtc.pyqtSignal(int)
    blinkerStop = qtc.pyqtSignal()
    # The following signal is local
    nextEvent = qtc.pyqtSignal(int)

    buzzInstace = vlc.Instance()
    buzzPlayer = buzzInstace.media_player_new()
    # toneEvents = tonePlayer.event_manager()
    # media = buzzInstace.media_new_path("/home/piswitch/Apps/sb-audio/buzzer.mp3")
    # buzzPlayer.set_media(media)
    buzzPlayer.set_media(buzzInstace.media_new_path("/home/piswitch/Apps/sb-audio/buzzer.mp3"))

    toneInstace = vlc.Instance()
    tonePlayer = toneInstace.media_player_new()
    toneEvents = tonePlayer.event_manager()
    toneMedia = toneInstace.media_new_path("/home/piswitch/Apps/sb-audio/outgoing-ring.mp3")
    tonePlayer.set_media(toneMedia)

    vlcInstances = [vlc.Instance(), vlc.Instance()]
    vlcPlayers = [vlcInstances[0].media_player_new(), vlcInstances[1].media_player_new()]
    vlcEvents = [vlcPlayers[0].event_manager(), vlcPlayers[1].event_manager()]

    def __init__(self):
        super().__init__()
        self.callInitTimer = qtc.QTimer()
        self.callInitTimer.setSingleShot(True)
        self.callInitTimer.timeout.connect(self.initiateCall)
        # reconnectTimer = undefined
        # audioCaption = " "
        self.nextEvent.connect(self.setTimeToNext)
        self.reset()

    def reset(self):
        self.stopAllAudio()

        # Put pinsIn here in model where it's used more often
        # rather than in control which would require a lot of signaling.
        self.pinsIn = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]
        self.currConvo = 0
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
                "callee": {"index": 99, "isPlugged": False}
                # "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
            },
            {
                "isEngaged": False,
                "unPlugStatus": self.NO_UNPLUG_STATUS,
                "caller": {"index": 99, "isPlugged": False},
                "callee": {"index": 99, "isPlugged": False}
                # "audioTrack": vlc.MediaPlayer("/home/piswitch/Apps/sb-audio/1-Charlie_Operator.mp3")
            }
        ]

        self.displayText.emit("Keep your ears open for incoming calls!")

    def stopAllAudio(self):
        # if self.callInitTimer.isActive():
        #     self.callInitTimer.stop()

        self.buzzPlayer.stop()
        self.tonePlayer.stop()
        self.vlcPlayers[0].stop()
        self.vlcPlayers[1].stop()

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
            # buzzTrack.volume = .6   
            self.buzzPlayer.play()
            self.blinkerStart.emit(conversations[self.currConvo]["caller"]["index"])
            self.displayText.emit("Incoming call..")
            
            print('-- New call being initiated by: ' + 
                persons[conversations[self.currConvo]["caller"]["index"]]["name"])
        else:
            # Play congratulations
            print("Congratulations - done!")
            # self.phoneLines[0].audioTrack =
            #     new Audio("https://dev.digitalgizmo.com/msm-ed/ed-assets/audio/FinishedActivity.mp3")
            #     phoneLines[0].audioTrack.play()
            # Probably reset as well

    def playHello(self, _currConvo, lineIndex):
        media = self.vlcInstances[lineIndex].media_new_path("/home/piswitch/Apps/sb-audio/" + 
            conversations[_currConvo]["helloFile"] + ".mp3")
        self.vlcPlayers[lineIndex].set_media(media)
        self.vlcPlayers[lineIndex].play()
        # Send msg to screen
        self.displayText.emit(conversations[_currConvo]["helloText"])


    def playConvo(self, currConvo, lineIndex):
        """
        This just plays the outgoing tone and then starts the full convo
        """
        print(f"got to play convo, lineIndex: {lineIndex}, currConvo: {currConvo}")
        # Long VLC way of creating callback
        # reassign event each time
        # self.toneEvents.event_detach(vlc.EventType.MediaPlayerEndReached)



        self.toneEvents.event_attach(vlc.EventType.MediaPlayerEndReached, 
            self.playFullConvo, currConvo, lineIndex) # playFullConvo(currConvo, lineIndex)
        

        self.tonePlayer.set_media(self.toneMedia)


        self.tonePlayer.play()

    def playFullConvo(self, event, _currConvo, lineIndex):
        # print(f"fullconvo, convo: {_currConvo}, linedx: {lineIndex}, dummy: {dummy}")
        # self.outgoingTone.stop()
        self.displayText.emit(conversations[_currConvo]["convoText"])


        # self.toneEvents.clear()

        print(f"playFullConvo, lineIndex: {lineIndex}")
        # Simulate callback for convo track finish
        self.vlcEvents[lineIndex].event_attach(vlc.EventType.MediaPlayerEndReached, 
            self.setCallCompleted,lineIndex) #  _currConvo, 

        media = self.vlcInstances[lineIndex].media_new_path("/home/piswitch/Apps/sb-audio/" + 
            conversations[_currConvo]["convoFile"] + ".mp3")

        self.vlcPlayers[lineIndex].set_media(media)
        self.vlcPlayers[lineIndex].play()

    def setTimeToNext(self, timeToWait):
        self.callInitTimer.start(timeToWait)        


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
                # self.buzzTrack.stop()
                self.buzzPlayer.stop()

                self.blinkerStop.emit()

                # start incoming request
                self.playHello(self.currConvo, self.whichLineInUse)

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

    def setCallCompleted(self, event, lineIndex): #, _currConvo, lineIndex


        # self.vlcEvents.clear() # Prevents mulitple calls to setCallCompleted



        #  let otherLineIdx = (lineIndex === 0) ? 1 : 0;
        # 'true' if True else 'false'
        otherLineIdx = 1 if (lineIndex == 0) else 0
        print(f"setCallCompleted() - line:  {lineIndex} stopping, other line has unplug stat of {self.phoneLines[otherLineIdx]['unPlugStatus']}")
        # Stop call
        self.stopCall(lineIndex)

        # Much intervening logic to handle call interruption



        self.currConvo += 1
        # Use signal rather than calling callInitTimer bcz threads
        # print("signal next event to time to next")
        self.nextEvent.emit(1000)




    def stopCall(self, lineIndex):
        self.clearTheLine(lineIndex)
        # Reset volume -- in this line was silenced by interrupting call


    def clearTheLine(self, lineIdx):
        # Clear the line settings
        self.phoneLines[lineIdx]["caller"]["isPlugged"] = False
        self.phoneLines[lineIdx]["callee"]["isPlugged"] = False
        self.phoneLines[lineIdx]["isEngaged"] = False
        self.phoneLines[lineIdx]["unPlugStatus"] = self.NO_UNPLUG_STATUS
        self.prevLineInUse = -1
        # Turn off the LEDs
        # persons[phoneLines[lineIdx].caller.index].ledState = LED_OFF;
        # self.ledEvent.emit(personIdx, False)
        self.ledEvent.emit(self.phoneLines[lineIdx]["caller"]["index"], False)
        # Can't turn off callee led if callee index hasn't been defined
        # console.log('phoneLines[lineIdx].callee.index: '+ phoneLines[lineIdx].callee.index);
        if (self.phoneLines[lineIdx]["callee"]["index"]):
            # console.log('got into callee index not null');
            self.ledEvent.emit(self.phoneLines[lineIdx]["callee"]["index"], False)
		


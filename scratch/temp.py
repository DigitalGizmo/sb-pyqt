from PySide.QtCore import QObject, Signal, Slot

class PunchingBag(QObject): 
    ''' Represents a punching bag; when you punch it, it emits a signal that indicates that it was punched. ''' 

    punched = Signal()

def __init__(self): # Initialize the PunchingBag as a QObject QObject.__init__(self)

    def punch(self): 
        ''' Punch the bag ''' 
    self.punched.emit()
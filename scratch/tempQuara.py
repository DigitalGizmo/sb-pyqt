from PyQt5.QtCore import QObject, pyqtSignal

class MyEmitter(QObject):
    # Define the custom signal
    my_signal = pyqtSignal(str)

    emitter = MyEmitter()
    emitter.my_signal.emit("Custom signal emitted!")


"""Separately, I think """
def my_slot(message):
    print("Received signal:", message)
    emitter.my_signal.connect(my_slot)
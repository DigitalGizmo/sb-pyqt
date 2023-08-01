import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

class FormWindow(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())

        self.edit = qtw.QLineEdit()
        self.submit = qtw.QPushButton('Submit', clicked=self.onSubmit)

        self.otherbutton = qtw.QPushButton('Other', clicked=self.onOther)

        self.layout().addWidget(self.edit)
        self.layout().addWidget(self.submit)
        self.layout().addWidget(self.otherbutton)

    def onSubmit(self):
        self.submitted.emit(self.edit.text())
        # self.close()

    def onOther(self):
        self.submitted.emit('I did this')
        # self.close()

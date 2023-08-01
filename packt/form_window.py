import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

from form_sub_window import FormWindow


class MainWindow(qtw.QWidget):

    def __init__(self):
        """MainWindow constructor.

        This widget will be our main window.
        We'll define all the UI components in here.
        """
        super().__init__()
        # Main UI code goes here

        self.setLayout(qtw.QVBoxLayout())

        self.label = qtw.QLabel('Click "change" to change this text.')

        # self.change = qtw.QPushButton('Change', clicked=self.onChange)
        # self.quitbutton.clicked.connect(self.close)
        # self.layout().addWidget(self.quitbutton)


        # self.entry1 = qtw.QLineEdit()
        # self.entry2 = qtw.QLineEdit()
        self.layout().addWidget(self.label)
        # self.layout().addWidget(self.change)
        # self.entry1.textChanged.connect(self.entry2.setText)

        # self.entry1.editingFinished.connect(lambda: print('editing finished'))
        # self.entry2.returnPressed.connect(self.entry1.editingFinished)

        # End main UI code
        self.show()

        # Set up formwindow automatically
        self.formwindow = FormWindow()
        # self.formwindow.submitted.connect(self.label.setText)
        self.formwindow.submitted.connect(self.handleInput)
        self.formwindow.show()   

    # def onChange(self):
    def handleInput(self, input):
        print('got to handle input')
        self.label.setText(input)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    # it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.
    mw = MainWindow()
    sys.exit(app.exec())

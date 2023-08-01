import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class MainWindow(qtw.QWidget):

    def __init__(self):
        """MainWindow constructor.

        This widget will be our main window.
        We'll define all the UI components in here.
        """
        super().__init__()
        # Main UI code goes here

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        # self.quitbutton = qtw.QPushButton('Quit')
        # self.quitbutton.clicked.connect(self.close)
        # self.layout().addWidget(self.quitbutton)


        self.entry1 = qtw.QLineEdit()
        self.entry2 = qtw.QLineEdit()
        self.layout().addWidget(self.entry1)
        self.layout().addWidget(self.entry2)
        # self.entry1.textChanged.connect(self.entry2.setText)

        self.entry1.editingFinished.connect(lambda: print('editing finished'))
        self.entry2.returnPressed.connect(self.entry1.editingFinished)


        # End main UI code
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    # it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.
    mw = MainWindow()
    sys.exit(app.exec())

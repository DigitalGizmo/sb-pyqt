import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

from panel import Panel


class MainWindow(qtw.QWidget):

    def __init__(self):
        """MainWindow constructor.

        This widget will be our main window.
        We'll define all the UI components in here.
        """
        super().__init__()

        self.setLayout(qtw.QVBoxLayout())

        self.label = qtw.QLabel('Keep your ears open!')

        self.layout().addWidget(self.label)

        self.show()

        # Set up panel
        self.panel = Panel()
        # self.panel.submitted.connect(self.label.setText)
        self.panel.submitted.connect(self.handleInput)

        

        self.panel.show()   




    # def onChange(self):
    def handleInput(self, input):
        print(f"got to handle input: {input}")
        self.label.setText(input)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    # it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.
    mw = MainWindow()
    sys.exit(app.exec())

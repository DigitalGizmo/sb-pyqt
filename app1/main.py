import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

from panel_bak import Panel


class MainWindow(qtw.QMainWindow):

    def __init__(self):
        """MainWindow constructor.
        This widget will be our main window.
        We'll define all the UI components in here.
        """
        super().__init__()

        self.setWindowTitle("You Are the Operator")
        # self.setLayout(qtw.QVBoxLayout())
        self.label = qtw.QLabel('Keep your ears open!')
        self.label.setAlignment(qtc.Qt.AlignTop)
        self.setCentralWidget(self.label)

        # self.layout().addWidget(self.label)
        self.setGeometry(20,120,600,200)
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

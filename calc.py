import sys
from PyQt5.QtWidgets import (
    QApplication, 
    QLabel, 
    QWidget
)

app = QApplication([])

window = QWidget()
window.setWindowTitle("pyqt app")
window.setGeometry(100,100,280,80)
helloMsg = QLabel("<h1> Hello, Hello </h1>", parent=window)
helloMsg.move(60, 15)

window.show()
sys.exit(app.exec())
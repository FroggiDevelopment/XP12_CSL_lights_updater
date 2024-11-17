# For later builds if possible
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox


class UpdaterInfo(QMainWindow):
    def __init__(self, title, message):
        super().__init__()

        self.type = type
        self.message = message

        self.setWindowTitle("My App")
        infobox = QMessageBox.information(
            self,
            title,
            message,
            buttons=QMessageBox.Ok,
        )
        self.setCentralWidget(infobox)


app = QApplication(sys.argv)
window = UpdaterInfo("Info", "Fertig!")
window.show()
sys.exit(app.exec())

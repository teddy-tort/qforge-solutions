import sys
from PySide6.QtWidgets import QMainWindow, QApplication

from __feature__ import snake_case, true_property

import pyqtgraph as pg


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # super(MainWindow, self).__init__()
        self.plot1 = pg.PlotWidget()
        # self.setCentralWidget(self.plot1)
        self.set_central_widget(self.plot1)
        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        self.plot1.plot(hour, temperature)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())

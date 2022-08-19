"""
Qt GUI application that can open and plot data live as it is generated.

author: Teddy Tortorici
"""

import get
import os
import sys
import time
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QToolBar, QMessageBox, QStyle, QFileDialog, QDialog,
                               QVBoxLayout, QDialogButtonBox, QLabel)
from PySide6.QtCore import Slot, Signal, Qt
from PySide6.QtGui import QIcon, QAction
import threading
import numpy as np
import pyqtgraph as pg


class PlotUpdater(QWidget):
    update_signal = Signal()


class PlotApp(QMainWindow):

    window_colors = {'background': (255, 255, 230),
                     'foreground': (0, 0, 0)}
    width = 1200
    height = 650
    pen_colors = [(155, 0, 0),          # dark red
                  (76, 145, 0),         # dark green
                  (0, 0, 200),          # dark blue
                  (122, 23, 220),       # purple
                  (204, 102, 0),        # dark orange
                  (0, 204, 204),        # cyan
                  (288, 104, 232)]      # magenta

    def __init__(self):
        QMainWindow.__init__(self)

        self.base_path = get.google_drive()
        self.filename = None
        self.update_thread = None
        self.force_quit = True
        self.live_plotting = True
        self.active_file = False
        self.plot_updater = PlotUpdater()
        self.plot_updater.update_signal.connect(self.update_plots)

        for key in PlotApp.window_colors.keys():
            pg.setConfigOption(key, PlotApp.window_colors[key])

        """WINDOW PROPERTIES"""
        self.setWindowTitle("Live Plotting App")
        self.resize(PlotApp.width, PlotApp.height)
        self.setWindowIcon(QIcon(os.path.join('icons', 'app.png')))

        self.plot = pg.PlotWidget()
        self.setCentralWidget(self.plot)

        self.curves = [None]
        self.pens = [None]

        """MENU BAR and TOOLBAR"""
        main_menu = self.menuBar()
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        file_menu = main_menu.addMenu('&File')
        plot_menu = main_menu.addMenu('&Plot')
        help_menu = main_menu.addMenu('&Help')

        # make File actions
        self.open_action = QAction(self.icon('DirIcon'), '&Open Data File', self)
        self.open_action.setShortcut('CTRL+O')
        self.open_action.triggered.connect(self.open_file)

        self.close_action = QAction(self.icon('TitleBarCloseButton'), '&Close Data File', self)
        self.close_action.setShortcut('CTRL+W')
        self.close_action.triggered.connect(self.close_file)
        self.close_action.setEnabled(False)

        self.quit_action = QAction(self.icon('BrowserStop'), 'E&xit App', self)
        self.quit_action.setShortcut('CTRL+Q')
        self.quit_action.triggered.connect(self.quit)

        # make Plot actions
        self.live_plot_action = QAction(self.icon('DialogYesButton'), 'Live &Plotting (turn off)', self)
        self.live_plot_action.setShortcut('CTRL+SPACE')
        self.live_plot_action.triggered.connect(self.swap_live)

        self.update_plots_action = QAction(self.icon('BrowserReload'), '&Update Plots', self)
        self.update_plots_action.setShortcut('CTRL+R')
        self.update_plots_action.triggered.connect(self.update_plots)
        self.update_plots_action.setEnabled(False)

        # make Help actions
        self.help_action = QAction(self.icon('MessageBoxQuestion'), 'User &Guide')
        self.help_action.setShortcut('CTRL+/')
        self.help_action.triggered.connect(self.get_help)

        file_menu_actions = [self.open_action, self.close_action, None, self.quit_action]
        plot_menu_actions = [self.live_plot_action, self.update_plots_action]
        help_menu_actions = [self.help_action]
        all_menus = [file_menu, plot_menu, help_menu]
        all_actions = [file_menu_actions, plot_menu_actions, help_menu_actions]

        for action_list, menu in zip(all_actions, all_menus):
            for action in action_list:
                if action:
                    menu.addAction(action)
                    if action.text() not in ['E&xit App', '&Close Data File']:
                        toolbar.addAction(action)
                else:
                    menu.addSeparator()
            toolbar.addSeparator()

    def run(self):
        while self.active_file:
            while self.live_plotting:
                self.plot_updater.update_signal.emit()
                time.sleep(1)
            time.sleep(1)

    @Slot()
    def open_file(self):
        """Open csv file to plot"""
        if self.active_file:
            self.close_file()
        if not self.active_file:
            filename, _ = QFileDialog.getOpenFileName(self, "Select Data Set", self.base_path,
                                                      "CSV (*.csv);;All Files (*)")
            if filename:
                self.close_action.setEnabled(True)
                self.active_file = True
                self.set_live_plotting(True)
                self.filename = filename
                # Make it so next time you open in the same place you left off
                # This removes the file from the path
                # Applying join(list) to a string makes a string where every element of the list is put
                # together with the string between them.
                # By taking [:-1] we leave out the last element of the list
                self.base_path = os.sep.join(filename.split(os.sep)[:-1])
                col_labels = self.get_labels()
                self.plot.setLabel('bottom', col_labels[0])
                self.plot.setLabel('left', col_labels[1])

                # optionally set legend if there are enough columns to justify it.
                if len(col_labels) > 2:
                    self.plot.addLegend()

                # handle the axis as a time axis if time is in the label name.
                if 'time' in col_labels[0].lower():
                    self.plot.setAxisItems({'bottom': pg.DateAxisItem('bottom')})

                # Make curves and pens have as many elements are there are Y columns
                y_num = len(col_labels) - 1
                self.curves *= y_num
                self.pens *= y_num
                for ii, label in enumerate(col_labels[1:]):
                    self.pens[ii] = pg.mkPen(PlotApp.pen_colors[ii], width=2, style=Qt.SolidLine)
                    self.curves[ii] = self.plot.plot(pen=self.pens[ii], name=label, symbol='o', symbolSize=5)

                self.update_thread = threading.Thread(target=self.run)
                self.update_thread.start()

    @Slot()
    def swap_live(self):
        """Turns live plotting off if on, and on if off"""
        self.set_live_plotting(not self.live_plotting)

    def set_live_plotting(self, on: bool):
        self.live_plotting = on
        self.update_plots_action.setEnabled(not on)
        if on:
            self.live_plot_action.setIcon(self.icon('DialogYesButton'))
            self.live_plot_action.setToolTip('Click to turn off Live Plotting')
            self.live_plot_action.setText('Live &Plotting (turn off)')
        else:
            self.live_plot_action.setIcon(self.icon('DialogNoButton'))
            self.live_plot_action.setToolTip('Click to turn on Live Plotting')
            self.live_plot_action.setText('Live &Plotting (turn on)')

    def load_data(self, attempts: int = 10) -> np.ndarray:
        """Loads data from filename. Will make attempts to load data while skipping an
        increasing number of rows each time. Will give up after 10 attempts"""
        data = None
        for attempt in range(attempts):
            try:
                data = np.loadtxt(self.filename, comments='#', delimiter=',', skiprows=attempt)
                break
            except ValueError:
                pass
        return data

    @Slot()
    def update_plots(self):
        """Updates the plots if live plotting is off."""
        if self.active_file:
            data = self.load_data()
            if len(data.shape) > 1:     # then we have loaded a data set
                x = data[:, 0]          # grabs first column
                ys = data[:, 1:]        # grabs the rest of the columns

                for ii, curve in enumerate(self.curves):
                    curve.setData(x=x, y=ys[:, ii])

    @Slot()
    def close_file(self):
        """Exits current data file for plotting"""
        close_question = QMessageBox.critical(self, 'Closing File',
                                              'Are you sure you would like to close this data file?',
                                              QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if close_question == QMessageBox.Yes:
            self.active_file = False
            self.set_live_plotting(False)
            self.update_thread.join()

            self.filename = None
            self.pens = [None]
            self.curves = [None]
            self.update_thread = None

            self.plot = pg.PlotWidget()
            self.setCentralWidget(self.plot)

    @Slot()
    def get_help(self):
        """Opens help dialog"""
        HelpPrompt().exec()

    @Slot()
    def quit(self):
        """Exits the application"""
        if self.active_file:
            self.close_file()
        if not self.active_file:
            exit_question = QMessageBox.critical(self, 'Exiting', 'Are you sure you would like to quit?',
                                                 QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
            if exit_question == QMessageBox.Yes:
                self.force_quit = False
                print('Exiting')
                self.close()

    def closeEvent(self, event):
        if self.force_quit:
            event.ignore()
            self.quit()
        else:
            event.accept()

    def icon(self, icon_name: str) -> QIcon:
        return QIcon(self.style().standardIcon(getattr(QStyle, f'SP_{icon_name}')))

    def get_labels(self, comment: str = '#') -> list:
        """Retrieves first line from file which is not commented out with a #
        returns a list of strings that are the labels for the columns"""
        with open(self.filename, 'r') as f:
            for ii in range(50):  # number in range will be how many attempts
                label_line = f.readline()
                if label_line[0] != comment:
                    break
        labels = label_line.rstrip('\n').replace("'", "").split(',')
        return [label.strip(" ") for label in labels]


class HelpPrompt(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("About")
        self.setWindowIcon(PlotApp.icon(self, 'MessageBoxQuestion'))

        """Main text"""
        text = 'This application allows you to open a csv file for plotting.\n' \
               'It will automatically update the plot as the csv file is appended to if the Live\n' \
               'Plotting setting is active (green circle). When it is not active (red circle),\n' \
               'you can manually update the plot by pressing the update button (looks like a\n' \
               'browser refresh icon).'
        main_label = QLabel(text)

        """Place button at end"""
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_label)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = PlotApp()
    main_window.show()

    sys.exit(app.exec())

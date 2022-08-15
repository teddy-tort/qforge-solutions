from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QToolButton
from PySide6.QtCore import Slot
import gui.built_in as built_in
from gui.plotting import Plot, RightAxisPlot
import sys
import pyqtgraph as pg


class PlotTab(QWidget):
    def __init__(self, parent, link_x=True, link_y=False):
        QWidget.__init__(self)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.live_plotting = True

        self.parent = parent

        self.filename = None

        main_layout = QHBoxLayout(self)
        plot_layout = QGridLayout()
        button_layout = QVBoxLayout()

        self.plot_TvV = Plot('Voltage (V)', 'Temperature (K)')
        self.plot_CvT = Plot('Temperature (K)', 'Voltage (V)')
        self.plot_Tvt = Plot('Time', 'Temperature (K)', date_axis_item=True)
        self.plot_Vvt = RightAxisPlot('Voltage (V)')
        self.plot_Cvt = Plot('Time', 'Counts', right_axis=self.plot_Vvt, date_axis_item=True)

        # Will place in the gid to mimic the list of lists
        plots = [[self.plot_TvV, self.plot_Tvt],
                 [self.plot_CvT, self.plot_Cvt]]

        """Link X and Y axes (if specified)"""
        if link_x or link_y:
            plot_list = [plot for plot_row in plots for plot in plot_row]       # flattens list of lists into a list
            for ii, plot_ii in enumerate(plot_list):
                for jj, plot_jj in enumerate(plot_list):
                    if ii < jj:
                        if link_x:
                            if plot_ii.x_label.lower() == plot_jj.x_label.lower():
                                plot_ii.setXLink(plot_jj)
                        if link_y:
                            if plot_ii.y_label.lower() == plot_jj.y_label.lower():
                                plot_ii.setYLink(plot_jj)

        """Place Plots in the grid layout"""
        for ii, plot_row in enumerate(plots):
            for jj, plot in enumerate(plot_row):
                plot_layout.addWidget(plot, ii, jj)

        """Place buttons in vertical layout"""
        self.button_update = QToolButton()
        self.button_update.setIcon(built_in.icon(self, 'BrowserReload'))
        self.button_update.setToolTip('Update Plots')
        self.button_update.clicked.connect(self.update_plots)

        self.button_play_pause = QToolButton()
        self.button_play_pause.clicked.connect(self.swap_live)
        self.set_live_plotting(True)

        buttons = [self.button_play_pause, self.button_update]
        for button in buttons:
            button_layout.addWidget(button)
        button_layout.addStretch(0)

        """Place layouts in main layout"""
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    @Slot(str)
    def initialize_plots(self, filename):
        self.filename = filename


    def set_live_plotting(self, on):
        self.live_plotting = on
        self.button_update.setEnabled(not on)
        if on:
            self.button_play_pause.setIcon(built_in.icon(self, 'DialogYesButton'))
            self.button_play_pause.setToolTip('Live Plotting')
        else:
            self.button_play_pause.setIcon(built_in.icon(self, 'DialogNoButton'))
            self.button_play_pause.setToolTip('Click to turn on Live Plotting')

    @Slot()
    def swap_live(self):
        self.set_live_plotting(not self.live_plotting)

    @Slot()
    def update_plots(self):
        pass


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    main_window = PlotTab(QWidget())
    main_window.show()

    sys.exit(app.exec())

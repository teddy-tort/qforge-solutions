from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QStackedWidget, QSizePolicy,
                               QDialog, QMessageBox, QFileDialog)
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QFont, QIcon
from gui.new_data_file_prompt import NewDataPrompt
import gui.built_in as built_in
from data_file import NewDataFile, OpenDataFile
from server import GpibServer
from client_tools import send as send_client
import threading
import time
import datetime


class WriteWidget(QWidget):
    """emits a message to a connected slot allowing you to write to the text box
    GUI's hate being altered from threads, and this is a way to avoid the issues associated with that"""
    output = Signal(str)

    def write(self, msg):
        self.output.emit(msg)


class PlotUpdaterWidget(QWidget):
    """emits signal to the plot to update"""
    update = Signal()
    initialize = Signal(str)

    def update_plots(self):
        self.update.emit()

    def init_plots(self, filename):
        self.initialize.emit(filename)


class DataTab(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent

        self.gpib_server = GpibServer(do_print=False)

        self.dialog = None
        self.data = None            # will be an object of a data file from data_file.py

        self.server_thread = None   # will create thread on data file start up
        self.data_thread = None     # will create thread on data file start up

        self.running = False
        self.active_file = False

        """So we can write to the GUI from threads"""
        self.writer = WriteWidget()
        self.writer.output.connect(self.write_from_thread)

        """So we can update plots when new data is taken"""
        self.plot_updater = None        # because parent.plot_tab isn't created until this is done initializing
        # Moved to activate_data_file()
        # self.plot_updater = PlotUpdaterWidget()
        # self.plot_updater.update.connect(self.parent.plot_tab.update_plots)
        # self.plot_updater.initialize.connect(self.parent.plot_tab.initialize_plots)

        """Create the layout of what goes in this tab"""
        self.layout = QVBoxLayout(self)

        self.data_text_stream = QTextEdit()     # this will be where data gets printed as it's collected
        self.data_text_stream.setReadOnly(True)
        self.data_text_stream.setFont(QFont('Arial', 12))

        self.bottom_row = QHBoxLayout()         # this will be a row to add widgets to bellow the text stream
        self.bottom_row.addStretch(1)

        self.button_new_data = QPushButton("Create New Data File")
        self.button_new_data.setIcon(built_in.icon(self, 'FileIcon'))
        self.button_new_data.clicked.connect(self.make_new_file)

        self.button_open_data = QPushButton("Open Data File")
        self.button_open_data.setIcon(built_in.icon(self, 'DirIcon'))
        self.button_open_data.clicked.connect(self.open_file)

        self.button_play_pause = QStackedWidget(self)
        self.button_play_pause.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.button_pause = QPushButton("Pause Data")
        self.button_pause.setIcon(built_in.icon(self, 'MediaPause'))
        self.button_pause.clicked.connect(self.pause_data)
        self.button_play = QPushButton("Take Data")
        self.button_play.setIcon(built_in.icon(self, 'MediaPlay'))
        self.button_play.clicked.connect(self.continue_data)
        self.button_play.setEnabled(False)
        self.button_pause.setEnabled(False)
        self.button_play_pause.addWidget(self.button_play)
        self.button_play_pause.addWidget(self.button_pause)

        self.button_stop = QPushButton("Stop")
        self.button_stop.setIcon(built_in.icon(self, 'MediaStop'))
        self.button_stop.setEnabled(False)
        self.button_stop.clicked.connect(self.stop)

        # add bottom row widgets to bottom_row
        self.bottom_row.addWidget(self.button_stop)
        self.bottom_row.addWidget(self.button_play_pause)
        self.bottom_row.addWidget(self.button_open_data)
        self.bottom_row.addWidget(self.button_new_data)

        """Add widgets to layout"""
        self.layout.addWidget(self.data_text_stream)
        self.layout.addLayout(self.bottom_row)

    def write(self, text):
        """Writes to the GUI by using the write_thread widget"""
        # print(f'sending "{text}" to thread')
        self.writer.write(text)

    @Slot(str)
    def write_from_thread(self, text):
        """Writes to GUI from the write_thread object attribute"""
        # print(f'received "{text}" fom thread')
        self.data_text_stream.append(text)
        # make the scroll bar scroll with the new text as it fills past the size of the window
        self.data_text_stream.verticalScrollBar().setValue(self.data_text_stream.verticalScrollBar().maximum())
        # self.data_text_stream.vertical_scroll_bar.set_value(self.data_text_stream.vertical_scroll_bar.maximum())

    @Slot()
    def open_file(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,  # parent
                                                     "Open data file",  # caption
                                                     self.parent.data_base_path,  # directory
                                                     "CSV (*.csv)",  # filters
                                                     options=options)  # dialog options
        if filename:
            # open file and read comment to find what the averaging setting is
            with open(filename, 'r') as f:
                for ii in range(2):                 # number in range will be which line is stored at the end
                    comment_line = f.readline()
            # see if average is specified in the comment
            self.dialog = FakeDialog()               # with default averaging_entry = 1
            if 'average' in comment_line:
                ave_num_end = comment_line.index('average') - 1
                # attempt to read the number of unknown size until it works
                for ii in range(3):
                    try:
                        self.dialog.averaging_entry = int(comment_line[ave_num_end-ii:ave_num_end])
                        break
                    except ValueError:
                        pass

            self.write(f'Opening file "{filename}"')
            self.write(f'Using averaging setting of {self.dialog.averaging_entry}')
            self.activate_data_file(filename)
            self.data = OpenDataFile(filename)
            self.data_thread.start()

    @Slot()
    def make_new_file(self):
        self.dialog = NewDataPrompt(self.parent.data_base_path)
        self.dialog.exec()

        if self.dialog.result() == QDialog.Accepted:
            creation_time = time.time()
            creation_datetime = datetime.datetime.fromtimestamp(creation_time)
            self.write('Starting new data file on {m:02}/{d:02}/{y:04} at {h:02}:{min:02}:{s}'.format(
                m=creation_datetime.month,
                d=creation_datetime.day,
                y=creation_datetime.year,
                h=creation_datetime.hour,
                min=creation_datetime.minute,
                s=creation_datetime.second))

            sample_name = self.dialog.sample_name_entry.replace(' ', '_')
            if not sample_name:
                sample_name = 'none'
            filename = '{sample}_{m:02}-{d:02}-{y:04}_{h:02}-{min:02}-{s}'.format(sample=sample_name,
                                                                                  m=creation_datetime.month,
                                                                                  d=creation_datetime.day,
                                                                                  y=creation_datetime.year,
                                                                                  h=creation_datetime.hour,
                                                                                  min=creation_datetime.minute,
                                                                                  s=creation_datetime.second)
            comment = 'Experiment performed on the {setup} setup with sample: {sample}.'.format(
                setup=self.dialog.setup_choice_entry,
                sample=self.dialog.sample_name_entry)
            if self.dialog.averaging_entry > 1:
                comment += f' Data is taken with {self.dialog.averaging_entry} averages.'
            if self.dialog.calibration_file_entry:
                comment += f' Using calibration file: {self.dialog.calibration_file_entry}.'
            if self.dialog.comment_entry:
                comment += f' ... {self.dialog.comment_entry}.'

            self.activate_data_file()
            self.data = NewDataFile(self.parent.data_base_path, filename, comment)
            self.data_thread.start()

    def activate_data_file(self, filename):
        self.server_thread = threading.Thread(target=self.gpib_server.run, args=())
        self.data_thread = threading.Thread(target=self.take_data, args=())

        self.plot_updater = PlotUpdaterWidget()
        self.plot_updater.update.connect(self.parent.plot_tab.update_plots)
        self.plot_updater.initialize.connect(self.parent.plot_tab.initialize_plots)
        self.plot_updater.init_plots(filename)

        self.active_file = True
        self.button_play.setEnabled(True)
        self.button_pause.setEnabled(True)
        self.button_stop.setEnabled(True)
        self.button_play_pause.setCurrentWidget(self.button_pause)
        self.button_new_data.setEnabled(False)
        self.button_open_data.setEnabled(False)
        self.parent.play_action.setEnabled(False)
        self.parent.pause_action.setEnabled(True)
        self.parent.stop_action.setEnabled(True)
        self.parent.new_file_action.setEnabled(False)
        self.parent.open_file_action.setEnabled(False)
        self.parent.exit_action.setEnabled(False)

        """Start GPIB communication server"""
        self.server_thread.start()
        time.sleep(0.01)

    def take_data(self):
        self.running = True
        while self.active_file:
            while self.running:
                data_point = self.data.take_data_point(ave=self.dialog.averaging_entry)
                print(f'Got this as data: {data_point}')
                self.data.write_row(data_point)
                self.write(str(data_point))
                if self.parent.plot_tab.live_plotting:
                    self.plot_updater.update_plots()

    @Slot()
    def continue_data(self):
        self.button_play_pause.setCurrentWidget(self.button_pause)
        self.button_pause.setEnabled(True)
        self.parent.pause_action.setEnabled(True)
        self.parent.play_action.setEnabled(False)
        self.running = True

    @Slot()
    def pause_data(self):
        self.button_play_pause.setCurrentWidget(self.button_play)
        self.button_play.setEnabled(True)
        self.parent.pause_action.setEnabled(False)
        self.parent.play_action.setEnabled(True)
        self.running = False
        self.write("Paused data taking.")

    @Slot()
    def stop(self):
        exit_question = QMessageBox.question(self, 'Stop', 'Are you sure you would like to close this data file?',
                                             QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if exit_question == QMessageBox.Yes:
            self.running = False
            self.active_file = False
            self.data_thread.join()
            self.button_stop.setEnabled(False)
            self.button_play_pause.setCurrentWidget(self.button_play)
            self.button_play.setEnabled(False)
            self.button_pause.setEnabled(False)
            self.button_open_data.setEnabled(True)
            self.button_new_data.setEnabled(True)
            self.parent.play_action.setEnabled(True)
            self.parent.pause_action.setEnabled(True)
            self.parent.stop_action.setEnabled(True)
            self.parent.new_file_action.setEnabled(False)
            self.parent.open_file_action.setEnabled(False)
            self.parent.exit_action.setEnabled(False)
            send_client('shutdown')
            self.server_thread.join()
            self.write("Closing File")
            self.data = None
            self.dialog = None


class FakeDialog:
    def __init__(self):
        self.averaging_entry = 1


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    main_window = DataTab(0)
    main_window.show()

    sys.exit(app.exec())

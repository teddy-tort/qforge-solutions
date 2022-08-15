from PySide6.QtWidgets import (QDialog, QGroupBox, QComboBox, QLineEdit, QPushButton, QSpinBox,
                               QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel, QFileDialog)
from PySide6.QtCore import Slot
import gui.built_in as built_in
import sys
import os
import yaml
import glob
import datetime
import time


class NewDataPrompt(QDialog):
    def __init__(self, base_path):
        QDialog.__init__(self)
        self.date = None            # fill when Okay is pressed
        self.base_path = base_path  # base path to where data is kept

        self.setWindowTitle("Measurement Details")
        self.setWindowIcon(built_in.icon(self, 'FileDialogInfoView'))

        self.form_group_box = QGroupBox("Enter Measurement Details")
        self.setup_choice = QComboBox()
        self.sample_name = QLineEdit()
        self.calibration_file = QPushButton()
        self.averaging = QSpinBox()
        self.comment = QLineEdit()

        # make 'presets' directory in data path if it's not there
        if not os.path.exists(os.path.join(self.base_path, 'presets')):
            os.makedir(os.path.join(self.base_path, 'presets'))

        # Try to get presets from a yaml file
        try:
            yaml_fname = max(glob.glob(os.path.join(self.base_path, 'presets', '*yml')), key=os.path.getctime)
            # tack the name on the end of the full path
            yaml_fname = os.path.join(self.base_path, 'presets', yaml_fname)
            print(f"Found most recent preset yaml file: {yaml_fname}")
            with open(yaml_fname, 'r') as f:
                preset_choices = yaml.safe_load(f)
        except ValueError:
            # This will happen if glob returns an empty string (there was no yaml file)
            preset_choices = {}

        # Try to retrieve preset choices
        try:
            self.setup_choice_entry = preset_choices['setup']
            self.sample_name_entry = preset_choices['sample']
            self.calibration_file_entry = preset_choices['cal']
            if not self.calibration_file_entry:
                self.calibration_file_entry = 'Click to find file'
            self.averaging_entry = preset_choices['ave']
            self.comment_entry = preset_choices['comment']
        except KeyError:
            # this will happen if there was no yaml file or the yaml file is incompatible and will put in default values
            self.setup_choice_entry = 'Main'
            self.sample_name_entry = ''
            self.calibration_file_entry = 'Click to find file'
            self.averaging_entry = 1
            self.comment_entry = ''

        """CREATE FORM"""
        layout = QFormLayout()

        # set default values
        self.setup_choice_options = ['Main', 'Secondary']
        self.setup_choice.addItems(self.setup_choice_options)
        self.setup_choice.setCurrentIndex(self.setup_choice_options.index(self.setup_choice_entry))

        self.sample_name.setText(self.sample_name_entry)

        self.calibration_file.setText(self.calibration_file_entry)
        self.calibration_file.clicked.connect(self.find_calibration)

        self.averaging.setValue(self.averaging_entry)

        self.comment.setText(self.comment_entry)

        # Create labels and descriptions
        labels = [(QLabel("Which Setup:"), "Select which experimental setup you're using", self.setup_choice),
                  (QLabel("Sample Name:"), "What sample is loaded into the experiment", self.sample_name),
                  (QLabel("Calibration Reference:"), "Select file to reference calibration", self.calibration_file),
                  (QLabel("Averaging:"), "How many measurements to average", self.averaging),
                  (QLabel("Comment:"), "Comment to put at the header of the data file", self.comment)]
        for label, description, fill_box in labels:
            label.whats_this = description
            layout.addRow(label, fill_box)

        self.form_group_box.setLayout(layout)

        """Place buttons at end"""
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_click)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.form_group_box)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    @Slot()
    def find_calibration(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,                              # parent
                                                  "Find Calibration",                # caption
                                                  self.base_path,                    # directory
                                                  "CSV (*.csv);;All Files (*)",      # filters
                                                  options=options)                   # dialog options
        self.calibration_file.setText(filename)


    @Slot()
    def accept_click(self):
        self.date = datetime.datetime.fromtimestamp(time.time())

        """Store entries from the fill boxes"""
        # retrieve string associated with index number
        self.setup_choice_entry = self.setup_choice_options[self.setup_choice.currentIndex()]

        self.sample_name_entry = self.sample_name.text()

        self.calibration_file_entry = self.calibration_file.text()
        # Make the entry blank if it's not a filepath!
        if os.sep not in self.calibration_file_entry:
            self.calibration_file_entry = ''

        self.averaging_entry = self.averaging.value()

        self.comment_entry = self.comment.text()

        """SAVE THESE SETTINGS FOR NEXT TIME"""
        presets_to_save = {'setup': self.setup_choice_entry,
                           'sample': self.sample_name_entry,
                           'cal': self.calibration_file_entry,
                           'ave': self.averaging_entry,
                           'comment': self.comment_entry}
        presets_filename = f'presets{self.date.year:04}-{self.date.month:02}-{self.date.day:02}_{self.date.hour:02}.yml'
        presets_filename = os.path.join(self.base_path, 'presets', presets_filename)
        with open(presets_filename, 'w') as f:
            yaml.dump(presets_to_save, f, default_flow_style=False)

        self.accept()


if __name__ == "__main__":
    import get
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = NewDataPrompt(os.path.join(get.google_drive(), 'data', 'fake'))
    sys.exit(dialog.exec())

"""
Contains importable tools for creating data files and taking data.

author: Teddy Tortorici
"""

import time
import os
import numpy as np
import get
# import device clients to communicate over the server, or device gpib classes to communicate directly
from lakeshore import Client as LakeShore
from fake_gpib_devices import FakeVoltageSupply, FakePhotonCounter


class CSVFile:

    file_type = ".csv"

    def __init__(self, path: str, name: str, comment: str = ""):
        """
        Create or open a csv file and manage it.
        :param path: file path to where you want to save the file
        :param name: name of the file you wish to create or open
        :param comment: an optional comment to put in the file
        """

        """MAKE SURE THE FILE NAME IS VALID"""
        name = name.rstrip(CSVFile.file_type)
        name = name.replace(".", "")
        name += CSVFile.file_type
        self.filename = os.path.join(path, name)

        """CHECK IF PATH TO FILE AND FILE EXIST"""
        # Check if path exists, if it doesn't, make all the directories necessary to make it
        if not os.path.isdir(path):
            os.makedirs(path)

        # Check if file exists, if it doesn't, make it
        if os.path.exists(self.filename):
            self.new = False
        else:
            self.new = True
            self.create_file()

        """APPEND OPTIONAL COMMENT"""
        if comment:
            self.write_comment(comment)

    def write_row(self, row_to_write: list):
        """Turns a list into a comma delimited row to write to the csv file"""
        with open(self.filename, 'a') as f:
            f.write(str(row_to_write).lstrip("[").rstrip("]") + '\n')

    def write_comment(self, comment: str):
        """Writes a comment line in the csv file"""
        with open(self.filename, "a") as f:
            f.write(f"# {comment}\n")

    def create_file(self):
        """Creates file by writing the first comment line"""
        with open(self.filename, "w") as f:
            f.write(f"# This data file was created on {time.ctime(time.time())}\n")


class DataFile(CSVFile):

    # set column labels here
    labels = ["Time (s)", "Temperature (K)", "Voltage (V)", "Frequency Hz"]

    def __init__(self, path: str, name: str, measurement_frequencies: list, comment: str = "", port: int = get.port):
        """
        Create or open a data file and manage it.
        :param path: file path to where you want to save the file
        :param name: name of the file you wish to create or open
        :param measurement_frequencies: list of frequencies that will be measured, given in Hz
        :param comment: an optional comment to put in the file
        :param port: the port to connect to communicate over
        """
        # This will open or create the file and give methods write_row(list) and write_comment(str)
        super(self.__class__, self).__init__(path, name, comment)

        """PLACE ALL DEVICES USED IN DATA ACQUISITION FOR THIS KIND OF DATA FILE HERE"""
        # Use client versions if you are communicating over a server to ensure no communication conflicts
        # Otherwise you can import direct versions of the classes to communicate directly with the devices
        self.ls = LakeShore(port=port)
        self.device = None                  # just a dummy object for demonstration

        """SET RUNNING PARAMETER"""
        # This parameter gives control over turning off while loops
        self.running = False

        """CREATE COLUMN LABELS BASED ON FREQUENCIES MEASURED AT"""
        # The number of columns will be equal to the number of labels specified in the class attribute times the number
        # of frequencies you measure at.
        self.measurement_frequencies = measurement_frequencies
        self.labels = [""] * (len(DataFile.labels) * len(measurement_frequencies))      # initiates self.labels
        self.get_labels()       # sets self.labels in method
        # Write labels to file if we created a new file
        if self.new:
            self.write_row(self.labels)

        """GET UNITS OF TEMPERATURE AS DEFINED IN THE CLASS LABELS"""
        # This is so if you change the label, it will automatically propagate that change
        # Get the index of the label that has "temperature" in it
        for ii, label in enumerate(DataFile.labels):
            temperature_label_index = ii
            if "temperature" in label.lower():
                break
        # gets the character in parentheses
        self.temperature_units = DataFile.labels[temperature_label_index].split('(')[1].split(')')[0]

    def take_data_continuous(self, print_data=True):
        """Takes data continuously until self.running is turned off"""
        self.running = True
        while self.running:
            data = self.sweep_frequencies()
            if print_data:
                print(data)
            self.write_row(data)

    def get_data_point(self, frequency: float) -> list:
        """Set experiment to a given frequency and make a measurement.
        Length of return list should be the same length as DataFile.labels"""
        # Set frequency on device
        self.device.set_frequency(frequency)

        temperature = self.ls.read_temperature(units=self.temperature_units)
        voltage = self.device.read_voltage()

        return [time.time(), temperature, voltage, frequency]

    def sweep_frequencies(self) -> list:
        """Takes a full data set by sweeping through the measurement_frequencies"""
        data = [0] * len(self.labels)
        for ff, frequency in enumerate(self.measurement_frequencies):
            # len(DataFile.labels) is the length of data you get from self.get_data_point(), so what's in the [] grabs
            # that many elements offset by ff times that amount.
            data[ff * len(DataFile.labels):(ff+1) * len(DataFile.labels)] = self.get_data_point(frequency)
        return data

    def get_labels(self):
        """Takes the labels from the class attribute and makes the object attribute repeat them for each measurement
        frequency."""
        for ff, frequency in enumerate(self.measurement_frequencies):
            # Change to appropriate units of frequency.
            # Changing the frequency variable does NOT change the elements in self.measurement_frequencies
            if frequency < 1e3:         # then Hz
                unit_modifier = ""
            elif frequency < 1e6:       # then kHz
                unit_modifier = "k"
                frequency /= 1e3
            elif frequency < 1e9:       # then MHz
                unit_modifier = "M"
                frequency /= 1e6
            elif frequency < 1e12:      # then GHz
                unit_modifier = "G"
                frequency /= 1e9
            elif frequency < 1e15:      # then THz
                unit_modifier = "T"
                frequency /= 1e12
            else:                       # then PHz
                unit_modifier = "P"
                frequency /= 1e15
            for ll, label in DataFile.labels:
                if "frequency" in label.lower():
                    self.labels[ff + ll] = label
                else:
                    self.labels[ff + ll] = f"{label} at {frequency} {unit_modifier}Hz"


class DataFileGuiExample(CSVFile):

    labels = ['Time [s]', 'Voltage [V]', 'Temperature [K]', 'Counts']

    def __init__(self, file_path: str, comment: str = '', port: int = get.port):
        """
        Creates (or opens if it the file name already exists) a data file for the GUI App example in Activity 8
        :param file_path: full path to file
        :param comment: an optional comment to write to the script
        :param port: the port number to connect to to communicate with the GPIB server
        """
        print(file_path)
        """CREATE OBJECTS FOR DEVICE CLIENTS"""
        self.ls = LakeShore(331, port=port)
        self.vs = FakeVoltageSupply()
        self.pc = FakePhotonCounter()

        path_list = file_path.split(os.sep)
        path = os.sep.join(path_list[:-1])
        name = path_list[-1]
        super(self.__class__, self).__init__(path, name, comment)

        if self.new:
            self.write_row(DataFileGuiExample.labels)

    def take_data_point(self, ave: int = 1):
        """Sweep through measurements and write them in a new row
        will average a number of data points if ave > 1"""
        ave = int(ave)
        times = np.zeros(ave)
        voltages = np.zeros(ave)
        temperatures = np.zeros(ave)
        counts = np.zeros(ave)
        for ii in range(ave):
            times[ii] = time.time()
            voltages[ii] = self.vs.read_voltage()
            temperatures[ii] = self.ls.read_temperature()
            counts[ii] = self.pc.read_counts()
        data_point = [sum(times)/ave, sum(voltages)/ave, sum(temperatures)/ave, sum(counts)/ave]
        self.write_row(data_point)
        return data_point

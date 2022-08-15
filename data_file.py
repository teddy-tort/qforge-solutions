import time
import os
import numpy as np
import get
from lakeshore import Client as LakeShore
from client_tools import DeviceClient


# This is just for the example, delete it for a working version
class FakeVoltageSupply(DeviceClient):
    def __init__(self):
        super(self.__class__, self).__init__('VS')

    def set_voltage(self, voltage):
        time.sleep(1)
        self.write(f'V: {voltage:.2f}')
        return f'Set voltage to {voltage:.2f}'

    def read_voltage(self):
        time.sleep(1)
        return self.query('V?')


class FakePhotonCounter(DeviceClient):
    def __init__(self):
        super(self.__class__, self).__init__('PC')

    def read_counts(self):
        time.sleep(1)
        return self.query('C?')


class OpenDataFile:
    def __init__(self, file_path, port=get.port):
        """Create instances of devices for server communication"""
        self.ls = LakeShore(331, port=port)     # lakeshore temperature controller
        self.vs = FakeVoltageSupply()           # a fake voltage supply working as an example placeholder
        self.pc = FakePhotonCounter()           # a fake photon counter working as an example placeholder

        """Create file"""
        self.full_name = file_path

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

    def write_row(self, row_to_write: list):
        """Turns a list into a comma delimited row to write to the csv file"""
        with open(self.full_name, 'a') as f:
            f.write(str(row_to_write).lstrip('[').rstrip(']') + '\n')

    def write_comment(self, comment: str):
        """Writes a comment line in the csv file"""
        with open(self.full_name, 'a') as f:
            f.write(f'# {comment}\n')


class NewDataFile(OpenDataFile):
    def __init__(self, path: str, filename: str, comment='', port=get.port):
        super(self.__class__, self).__init__(os.path.join(path, filename), port=port)
        if '.csv' not in self.full_name:
            self.full_name += '.csv'        # add extension if it's not given

        # Create header
        self.create_file()
        self.write_comment(comment)

        self.column_labels = ['Time [s]', 'Voltage [V]', 'Temperature [K]', 'Counts']

        self.write_row(self.column_labels)

    def create_file(self):
        with open(self.full_name, 'w') as f:
            f.write(f'# This file was created on {time.ctime(time.time())}\n')

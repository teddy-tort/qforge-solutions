import numpy as np
import time
import os


class DataFile:
    def __init__(self, path: str, name: str):
        if not os.path.isdir(path):
            os.makedirs(path)
        if '.csv' not in name:
            name += '.csv'
        self.filename = os.path.join(path, name)
        self.create_file()
        self.write_comment("THIS IS A FAKE DATA FILE!!")

        self.column_labels = ['Time [s]', 'Voltage [V]']

        self.write_row(self.column_labels)

    def run(self):
        while True:
            data = self.generate_data_point()
            print(data)
            self.write_row(data)
            time.sleep(0.5+np.random.random())

    @staticmethod
    def generate_data_point():
        now = time.time()
        voltage = 3*np.cos(now)+np.random.random()
        return [now, voltage]

    def write_row(self, row_to_write: list):
        """Turns a list into a comma delimited row to write to the csv file"""
        with open(self.filename, 'a') as f:
            f.write(str(row_to_write).lstrip('[').rstrip(']') + '\n')

    def write_comment(self, comment: str):
        """Writes a comment line in the csv file"""
        with open(self.filename, 'a') as f:
            f.write(f'# {comment}\n')

    def create_file(self):
        with open(self.filename, 'w') as f:
            f.write(f'# This FAKE data file was created on {time.ctime(time.time())}\n')


if __name__ == "__main__":
    import get
    data_file = DataFile(os.path.join(get.google_drive(), 'data', 'fake'), 'fake_{:d}.csv'.format(int(time.time())))
    data_file.run()

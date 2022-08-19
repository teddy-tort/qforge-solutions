"""
Example script for taking data

@author: Teddy
"""
import os
import sys
import time
from client_tools import send as send_to_server
from threading import Thread
from data_files import DataFile
from server import GpibServer
from lakeshore import Client as LakeShore


class Manager:

    commands = [("stop", "end script"),
                ("T=[xx.x] K", "set temperature to [xx.x] Kelvin")]
    path = os.path.join('data', 'fake')

    def __init__(self, filename):
        """
        Creates a data taking manager that runs an experiment but allows you to still interact with devices through
        user inputs
        :param filename: name the file
        """
        print("Type 'help' to get info")

        """ASSIGN DEVICES YOU WISH TO INTERACT WITH THROUGH THE USER INPUT PROMPT"""
        self.ls = LakeShore()

        """CREATE DATA FILE AND SERVER AND PUT THEM IN THREADS"""
        comment = "This data was generated from data_taking_example.py"
        self.data = DataFile(path=Manager.path, name=filename, comment=comment)
        self.server = GpibServer(do_print=False)
        self.data_taking_thread = Thread(target=self.data.take_data_continuous, args=(False,))
        self.server_thread = Thread(target=self.server.run)

    def start(self):
        """Runs the GPIB server and then starts taking data. Each is done in it's own thread"""
        self.server_thread.start()
        time.sleep(1)
        self.data_taking_thread.start()

    def stop(self):
        """Lets the program conclude"""
        self.data.running = False
        self.data_taking_thread.join()
        send_to_server(GpibServer.shutdown_command.decode())
        self.server_thread.join()

    def wait_for_input(self) -> str:
        """Waits for message"""
        user_message = input("Give a command: ")
        self.parse(user_message)
        return user_message

    def parse(self, message_to_parse: str):
        """Parses message and executes command if applicable"""
        if message_to_parse.lower() == "help":
            for command, command_info in Manager.commands:
                print(f"Type '{command}' to {command_info}")
        elif message_to_parse.lower() == "stop":
            self.stop()
            print("Exiting Program")
        elif message_to_parse[:2] == "T=":
            try:
                temperature = float(message_to_parse.upper().replace(" ", "").split("=")[1].lstrip("K"))
                self.ls.set_setpoint(temperature)
                print(f"Set temperature set-point to {temperature}")
            except ValueError:
                print("Invalid temperature value")
        else:
            print("Invalid command. Try 'help'")


if __name__ == "__main__":
    # sys.argv returns a list of strings. The first element is the name of the script, and the next elements are
    # commands passed after the script
    # For example: python data_taking_example.py some_stuff some_more_stuff
    # will make sys.argv = ["data_taking_example.py", "some_stuff", "some_more_stuff"]
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = f"data_example_{int(time.time()):d}.csv"

    manager = Manager(name)
    manager.start()
    while True:
        msg = manager.wait_for_input()
        if msg.lower() == "stop":
            break

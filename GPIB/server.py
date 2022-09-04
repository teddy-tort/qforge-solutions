"""
Server functions that allow us to communicate over sockets to control devices

author: Teddy Tortorici
"""

import time
import socket
import get
import gpib


class GpibServer:
    # "class attributes" go here
    shutdown_command = b"shutdown"  # the command that will shutdown the server (must be a bit string)

    def __init__(self, host: str = "localhost", port: int = 62538, silent=False):
        """
        Create a server object
        :param host: IP address of socket where server will be located
        :param port: port of socket where server will be located
        :param silent: option to allow you to "silence" all the print statements
        """
        self.host_port = (host, port)  # create the tuple that goes into socket.socket.bind()
        self.running = False  # when we create the object, we don't want the server to start running right away
        self.silent = silent

        """CREATE OBJECTS FOR DEVICES"""
        # all your devices will go here
        self.lakeshore = gpib.Device(get.gpib_address["LS"])

        """Add any set up commands you want to have done once the server starts running
        ie, you may want to set certain settings by default when the system starts up"""
        # Put start up commands to devices here; eg setting certain units, initial setpoints, ramping, etc

    def handle(self, message_to_parse: str) -> str:
        """
        Parse a message of the format [Device ID]::[command]::[optional message]
        :param message_to_parse: incoming message from a client
        :return: the response from the device
        """
        msg_list = message_to_parse.upper().split(
            '::')  # turn the string into a list, cutting it at the "::"s (also make sure it's uppercase)
        dev_id = msg_list[0]  # the first part of the string should be the device id
        command = msg_list[1]  # the command (read, write, query) should be the second
        # because having a message is optional, we want to try to get it, but if it's out of range for the list
        # we don't want it to crash
        try:
            message = msg_list[2]
        except IndexError:
            message = ""

        """MUST EDIT THE FOLLOWING LINES TO MATCH THE DEVICES YOU ARE USING"""
        if dev_id == "LS":
            device = self.lakeshore  # device acts like a "pointer" and essentially points to self.lakeshore
            dev_name = "Lakeshore Temperature Controller"
        # elif statments for other devices; for example:
        # elif dev_id == "VS":
        #    device = self.voltage_supply
        #    dev_name = "Keithley Voltage Supply"
        else:
            device = None
            dev_name = "Failed to find an instument"
        if not self.silent:
            print(f"Connecting to: {dev_name:s}")

        if device:
            # write to device
            if command[0] == "W":
                if not self.silent:
                    print(f'Writing "{message}" to {dev_id}')
                device.write(message)
                msgout = 'empty'

            # query device
            elif command[0] == "Q":
                if not self.silent:
                    print(f'Querying {dev_id} with "{message}"')
                msgout = device.query(message)

            # read from device
            elif command[0] == "R":
                if not self.silent:
                    print(f'Reading from {dev_id}')
                msgout = device.read()
        else:
            msgout = f'Did not give a valid device id: {dev_id}'
        return msgout

    def run(self):
        """
        Establishes a socket server which takes and handles commands
        """
        self.running = True  # set to true to allow the while loop to run

        # open a new socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # bind to the (host, port)
            s.bind(self.host_port)

            # confirm the socket is bound
            print(f"Socket bound to port: {self.host_port[1]}")

            # put the socket into listening mode
            s.listen()

            # loop until a client requests the server shutdown
            while self.running:
                # establish a connection with a client
                conn, addr = s.accept()

                # open the connection
                with conn:
                    if not self.silent:
                        print(f"Connected to: {addr[0]}:{addr[1]}  : {time.ctime(time.time())}")
                    while True:
                        msg_client = conn.recv(1024)
                        if not self.silent:
                            print(repr(msg_client))
                        if not msg_client:
                            break
                        elif msg_client == GpibServer.shutdown_command:
                            print('Received shutdown command')
                            self.running = False
                            break
                        else:
                            # decode the message from the client to make it a normal string
                            msg_client = msg_client.decode()
                            if not self.silent:
                                print(f'Received message: {msg_client}')

                            # put the client message through the handle method and get the response from the device
                            msg_server = self.handle(msg_client)

                            # encode as a bit string and send it back to the client
                            conn.sendall(msg_server.encode())


def server_echo_rev(host: str = "localhost", port: int = get.port):
    """Establishes a socket server which echos back at the the client witht the message reversed
    If it receives 'ping', will respond 'gnip'"""
    # set the while loop to begin running
    running = True

    # open a new socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))

        # confirm the socket is bound
        print(f"Socket bound to port: {port}")

        # put the socket into listening mode
        s.listen()

        # loop until a client requests the server shutdown
        while running:
            # establish a connetion with a client
            conn, addr = s.accept()
            with conn:
                print(f"Connected to: {addr[0]}:{addr[1]}  : {time.ctime(time.time())}")
                while True:
                    msg_client = conn.recv(1024)
                    print(repr(msg_client))
                    if not msg_client:
                        break
                    elif msg_client == b"shutdown":
                        running = False
                        break
                    else:
                        print(f'Received message: {msg_client.decode()}')
                        msg_server = msg_client.decode()[::-1]
                        conn.sendall(msg_server.encode())


if __name__ == "__main__":
    # server_echo_rev()
    server = GpibServer()
    server.run()

import serial
from serial.tools import list_ports


class Serial:
    def __init__(self, chip_name="Silicon"):
        self.chip_name = chip_name

    def search_ports(self):
        ports = []
        try:
            com_port_name = str(next(list_ports.grep(self.chip_name)))
            ports.append(com_port_name[0:4])
            return ports[0]
        except StopIteration:
            print("No found")


class Connect:
    def __init__(self, port):
        self.port = port

    def connect_port(self):
        connected_port = serial.Serial(self.port)
        return connected_port

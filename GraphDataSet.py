import random
import serial
import sys
import GUI
import threading
import SerialCommunicate
from matplotlib.lines import Line2D
from serial.tools import list_ports


class GraphData(object):
    def __init__(self, random_int=11, ax=None, pause=False):
        self.random_int = random_int
        self.ax = ax
        self.dt = 0
        self.max_x = 0
        self.x_data = [0]
        self.y_data = [0]
        # self.line = Line2D(self.x_data, self.y_data)

        self.available_ports = []
        self.port = ''
        self.pause = pause

        self.data_space = []

        # self.graph_data()

    def throw_data(self):
        while True:
            yield self.data_space[0]

    def graph_data(self):
        while True:
            data = random.randrange(self.random_int)
            if len(self.data_space) <= 50:
                self.data_space.append(data)
            else:
                del self.data_space[0]
            # print(self.data_space[0])
            # yield self.data_space[0]

    def battery_data(self):
        # graph_data = GraphDataSet.GraphData()
        serial_com = SerialCommunicate.Serial("Silicon")
        port = serial_com.search_ports()
        connect_port = SerialCommunicate.Connect(port)
        connected_port = connect_port.connect_port()

        data = connected_port.readline()
        # convert_str = data[:-2].decode()
        # print(convert_str)
        convert = float(data[:-2].decode())
        print(convert)

        while True:
            if len(self.data_space) <= 50:
                self.data_space.append(convert)
            else:
                del self.data_space[0]
                self.data_space.append(convert)
            print(self.data_space[0])

    def serial_port(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        else:
            raise EnvironmentError('Unsupported platform')

        for port in ports:
            try:
                serial_port = serial.Serial(port)
                serial_port.close()
                self.available_ports.append(port)
            except (OSError, serial.SerialException):
                pass

        # print(self.available_ports)
        return self.available_ports

    def draw_graph(self):
        timer = threading.Timer(0.5, self.draw_graph)
        port = search_port()
        connect_port = serial.Serial(port)
        data = connect_port.readline()
        convert_str = data[:-2].decode()
        convert_float = float(convert_str)

        if len(self.data_space) <= 10:
            self.data_space.append(convert_float)
        # print(self.battery_data)
        timer.start()


def search_port():
    ports = []
    try:
        com_port_name = str(next(list_ports.grep("Silicon")))
        ports.append(com_port_name[0:4])
        return ports[0]
    except StopIteration:
        print("No found")


"""
if __name__ == '__main__':
    graph_data = GraphData()
    t = threading.Thread(target=graph_data.graph_data)
    t.start()
"""

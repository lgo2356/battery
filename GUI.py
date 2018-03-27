import sys
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import GraphDataSet
import SerialCommunicate
import Label
import time
import threading
import random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets, QtCore, QtGui


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(600, 200, 1200, 600)
        self.setWindowTitle("DPLES Chart v0.1")

        self.widgets = Widgets(parent=None)
        self.setCentralWidget(self.widgets)

        self.port_menu_dic = {}

        self.menu()

    def menu(self):
        menu_bar = self.menuBar()
        graph_data = GraphDataSet.GraphData()
        available_ports = graph_data.serial_port()
        available_ports_len = len(available_ports)

        port_menu = menu_bar.addMenu('PORT')
        num = 0
        self.port_menu_dic = {num: available_ports[0]}
        action_list = []

        for port in available_ports:
            com_port = port
            self.port_menu_dic[num] = com_port
            action_list.append(QtWidgets.QAction('', self))
            action_list[num].setText(com_port)
            port_menu.addAction(action_list[num])
            num += 1


class Widgets(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph_fig = plt.figure()
        self.canvas = FigureCanvas(self.graph_fig)
        self.ax = None
        self.chk_battery1 = None
        self.pause = False

        self.data_space = []
        self.data_space2 = []
        self.connected_port = None
        self.label_battery_per = None
        self.battery_per_inner_layout = None
        self.super_layout = None

        self.battery_port()
        t = threading.Thread(target=self.battery_data())
        t.start()

        self.update_label()
        self.layout()
        self.test()

    def test(self):
        battery_per = self.battery_percent
        label = Label.Label(str(battery_per()))
        label_text = label.label_text()
        label_per = label_text + '%'
        timer = threading.Timer(1, self.test)
        self.label_battery_per.setText(label_per)
        # time.sleep(1)
        # self.label_battery_per.setText("test2")
        timer.start()

    def update_label(self):
        battery_per = self.battery_percent
        label = Label.Label(str(battery_per()))
        label_text = label.label_text()
        label_per = label_text + '%'
        self.label_battery_per = QtWidgets.QLabel("100%", self)
        self.label_battery_per.setText(label_per)
        self.label_battery_per.setAlignment(QtCore.Qt.AlignCenter)
        self.battery_per_inner_layout = QtWidgets.QVBoxLayout()
        self.battery_per_inner_layout.addWidget(self.label_battery_per)

    def layout(self):
        # Group Box
        groupbox_graph = QtWidgets.QGroupBox('그래프', self)
        groupbox_battery_index = QtWidgets.QGroupBox('배터리 목록', self)
        groupbox_battery_per = QtWidgets.QGroupBox('현재 배터리 용량', self)
        groupbox_battery_time = QtWidgets.QGroupBox('예상 배터리 가용 시간', self)
        groupbox_battery_avg_used_week = QtWidgets.QGroupBox('일주일 평균 사용량', self)
        groupbox_battery_avg_used_month = QtWidgets.QGroupBox('한 달 평균 사용량', self)
        # Group Box

        # Text Label
        label_battery_time = QtWidgets.QLabel('60분', self)
        label_battery_avg_used_week = QtWidgets.QLabel('70Wh', self)
        label_battery_avg_used_month = QtWidgets.QLabel('60Wh', self)
        # Image Label
        img = read_image('dples_logo.png')
        label_logo = QtWidgets.QLabel(self)
        label_logo.setPixmap(img)
        label_logo.resize(100, 100)

        # Sorting
        label_battery_time.setAlignment(QtCore.Qt.AlignCenter)
        label_battery_avg_used_week.setAlignment(QtCore.Qt.AlignCenter)
        label_battery_avg_used_month.setAlignment(QtCore.Qt.AlignCenter)
        # Label

        # Battery Index
        self.chk_battery1 = QtWidgets.QCheckBox('배터리1')
        self.chk_battery2 = QtWidgets.QCheckBox('배터리2')
        self.chk_battery3 = QtWidgets.QCheckBox('배터리3')

        self.chk_battery1.stateChanged.connect(self.chkbox_state)
        # Battery Index

        # Inner Layout
        graph_inner_layout = QtWidgets.QVBoxLayout()
        graph_inner_layout.addWidget(self.canvas)
        groupbox_graph.setLayout(graph_inner_layout)

        groupbox_battery_per.setLayout(self.battery_per_inner_layout)

        battery_time_inner_layout = QtWidgets.QVBoxLayout()
        battery_time_inner_layout.addWidget(label_battery_time)
        groupbox_battery_time.setLayout(battery_time_inner_layout)

        battery_avg_used_week_inner_layout = QtWidgets.QVBoxLayout()
        battery_avg_used_week_inner_layout.addWidget(label_battery_avg_used_week)
        groupbox_battery_avg_used_week.setLayout(battery_avg_used_week_inner_layout)

        battery_avg_used_month_inner_layout = QtWidgets.QVBoxLayout()
        battery_avg_used_month_inner_layout.addWidget(label_battery_avg_used_month)
        groupbox_battery_avg_used_month.setLayout(battery_avg_used_month_inner_layout)

        left_inner_layout = QtWidgets.QVBoxLayout()
        left_inner_layout.addWidget(self.chk_battery1)
        left_inner_layout.addWidget(self.chk_battery2)
        left_inner_layout.addWidget(self.chk_battery3)
        left_inner_layout.addStretch(1)
        left_inner_layout.setAlignment(QtCore.Qt.AlignCenter)
        groupbox_battery_index.setLayout(left_inner_layout)
        # Inner Layout

        # Outer layout
        graph_layout = QtWidgets.QVBoxLayout()
        graph_layout.addWidget(groupbox_graph)

        data_layout = QtWidgets.QVBoxLayout()
        data_layout.addWidget(groupbox_battery_per)
        data_layout.addWidget(groupbox_battery_time)
        data_layout.addWidget(groupbox_battery_avg_used_week)
        data_layout.addWidget(groupbox_battery_avg_used_month)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(groupbox_battery_index)

        graph_data_layout = QtWidgets.QVBoxLayout()
        graph_data_layout.addLayout(graph_layout)
        label_layout = QtWidgets.QVBoxLayout()
        label_layout.addLayout(data_layout)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(graph_data_layout)
        main_layout.addLayout(label_layout)
        main_layout.setStretchFactor(graph_data_layout, 15)
        main_layout.setStretchFactor(left_layout, 1)

        dplay_layout = QtWidgets.QHBoxLayout()
        dplay_layout.addWidget(label_logo)
        dplay_layout.addStretch(1)

        super_layout = QtWidgets.QVBoxLayout()
        super_layout.addLayout(dplay_layout)
        super_layout.addLayout(main_layout)
        # self.test()
        self.setLayout(super_layout)
        # Outer layout

    def battery_port(self):
        serial_com = SerialCommunicate.Serial("Silicon")
        port = serial_com.search_ports()
        connect_port = SerialCommunicate.Connect(port)
        self.connected_port = connect_port.connect_port()
        print(port)

    def battery_data(self):
        timer = threading.Timer(0.0001, self.battery_data)
        try:
            data = self.connected_port.readline()
            convert = float(data[:-2].decode())
            if len(self.data_space) <= 0:
                self.data_space.append(convert)
            else:
                del self.data_space[0]
                self.data_space.append(convert)
            print(self.data_space)
            timer.start()
        except Exception:
            print("Restart")
            self.battery_port()
            self.battery_data()

    def battery_percent(self):
        battery_data = self.data_space[0]
        battery_per = int((battery_data/4.25)*100)
        return battery_per

    def draw_graph(self):
        timer = threading.Timer(0.5, self.draw_graph)
        data = self.data_space[0]
        self.ax.clear()
        if self.pause is not True:
            if len(self.data_space2) <= 10:
                self.data_space2.append(data)
                self.ax.set_xlim(0, 10)
                self.ax.set_ylim(3.5, 4.5)
                self.ax.plot(self.data_space2)
                self.canvas.draw()
            else:
                del self.data_space2[0]
                self.data_space2.append(data)
                self.ax.set_xlim(0, 10)
                self.ax.set_ylim(3.5, 4.5)
                self.ax.plot(self.data_space2)
                self.canvas.draw()
            timer.start()
        else:
            timer.cancel()

    def chkbox_state(self):
        if self.chk_battery1.isChecked() is True:
            self.pause = False
            self.ax = self.graph_fig.add_subplot(111)
            self.draw_graph()
        elif self.chk_battery1.isChecked() is not True:
            self.ax.clear()
            self.pause = True


def read_image(img_name):
    img = QtGui.QPixmap('./Images/%s' % img_name)
    resize_height = img.height()/3
    img = img.scaledToHeight(int(resize_height))
    width = img.width()
    height = img.height()
    print(width, height)
    return img


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()

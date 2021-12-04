import matplotlib as matplotlib
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets, uic
import qdarkstyle
matplotlib.use('Qt5Agg')
from matplotlib.pyplot import isinteractive
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ErrorMap import ErrorMap, ThreadedErrorMap
import sys


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.fig.tight_layout()
        self.axes.grid()

class Main_window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main_window, self).__init__()
        uic.loadUi('Team7_on_fire.ui', self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        # Menu Bar
        self.menubar = self.findChild(QtWidgets.QMenuBar, "menubar")
        self.menuFile  = self.menubar.findChild(QtWidgets.QMenu,"menuFile")
        self.menuFile.addAction("open",self.open_file)
        #   =self.menuFile.findChild(QtWidgets.QAction,"actionoppppen")
        # print(type(self.openAction))

        # graph layout
        self.graph_layout = self.findChild(QtWidgets.QVBoxLayout, "graph_Layout")


        # Radio_butto_Layout
        # radio buttons
        self.one_chunk_button = self.findChild(QtWidgets.QRadioButton, "one_chunk")
        self.multiple_chunks_button = self.findChild(QtWidgets.QRadioButton, "mlutiple_chunks")

        # grid layout
        # sliders
        self.data_percentage_slider = self.findChild(QtWidgets.QSlider, "data_percentage_slider")
        self.number_of_chunks_slider = self.findChild(QtWidgets.QSlider, "number_of_chunks_slider")
        self.polynomial_degree_slider = self.findChild(QtWidgets.QSlider, "polynomial_degree_slider")
        self.sliders_arr = [self.data_percentage_slider, self.number_of_chunks_slider,self.polynomial_degree_slider]


        # lables
        self.data_percentage_label = self.findChild(QtWidgets.QLabel, "data_percentage_label")
        self.number_of_chunks_lable = self.findChild(QtWidgets.QLabel, "number_of_chunks_lable")
        self.degree_lable = self.findChild(QtWidgets.QLabel, "degree_lable")
        self.lables_arr =[ self.data_percentage_label, self.number_of_chunks_lable,
                                self.degree_lable]
        self.lable_3 = self.findChild(QtWidgets.QLabel, "label_3")

        #Buttons
        self.ploting_button = self.findChild(QtWidgets.QPushButton,"start_button")
        self.plotting_flag = True
        self.fitting_button = self.findChild(QtWidgets.QPushButton,"fitting_button")


        # canves widget
        self.canves  = MplCanvas()
        self.error_map  = ErrorMap()
        self.graph_layout.addWidget(self.canves )
        self.erro_map_layout.insertWidget(0, self.error_map)

        # init:
        self.init_visability_with_radio_buttons()

        # signals
        #   radio button(multiple)
        self.multiple_chunks_button.toggled.connect(self.setting_chunks_mode)
        #   signal func arr
        self.signals_func_arr = [lambda value , i =0:self.slider_updated(value,i),lambda value , i =1:self.slider_updated(value , i),
                                 lambda value , i =2:self.slider_updated(value , i) ]

        for i in range(len(self.sliders_arr)):
            self.sliders_arr[i].valueChanged.connect(self.signals_func_arr[i])

        # Plot button signal
        self.ploting_button.clicked.connect(self.plot_data)
        #self.fitting_button.clicked.connect(self.interpolation)

        # self.openAction.triggered.connect(self.open_file())

        self.error_map_button.clicked.connect(self.error_map_handler)
        self.error_map.ready.connect(self.toggleStartCancel)

        self.thread_error_map = ThreadedErrorMap()
        self.thread_error_map.currProgress.connect(self.update_progressbar)

    def init_visability_with_radio_buttons(self):
        self.one_chunk_button.setChecked(True)
        self.setting_chunks_mode()


    def setting_chunks_mode(self):
        if self.multiple_chunks_button.isChecked():
            self.number_of_chunks_slider.show()
            self.lable_3.show()
            self.number_of_chunks_lable.show()
        else:
            self.number_of_chunks_slider.hide()
            self.lable_3.hide()
            self.number_of_chunks_lable.hide()


    def slider_updated(self, value,i):
        self.lables_arr[i].setText(str(value))


    def open_file(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName()
        if filename:
            self.loaded_data = pd.read_csv(filename)
            self.x_scattered_points = self.loaded_data[self.loaded_data.columns[0]].to_numpy()
            self.y_scattered_points = self.loaded_data[self.loaded_data.columns[1]].to_numpy()

        print(self.x_scattered_points)

    def plot_data(self):
            if self.plotting_flag:
                self.canves.axes.plot(self.x_scattered_points, self.y_scattered_points, "-o")
                self.canves.draw()
                self.plotting_flag = False
                self.ploting_button.setText("Clear Scatterd Points")
            else:
                self.canves.axes.cla()
                self.canves.axes.grid()
                self.canves.draw()
                self.plotting_flag = True
                self.ploting_button.setText("Plot Scatterd Points")

    def getError(self,function_degree, no_of_chuncks):
        total_Residual = 0
        length_of_data = len(self.x_scattered_points)
        intervals = int(length_of_data / no_of_chuncks)
        for i in range(no_of_chuncks):
            coefficients, residual, _, _, _ = np.polyfit(self.x_scattered_points[i * intervals:intervals * (i + 1) - 1],
                                                         self.y_scattered_points[0 + i * intervals:intervals * (i + 1) - 1],
                                                         function_degree, full='true')
            total_Residual = total_Residual + residual
        return total_Residual / length_of_data

    def fitting_datd(self, function_degree, no_of_chuncks):
        coefficient_list = []
        length_of_data = len(self.x_scattered_points)
        intervals = int(length_of_data / no_of_chuncks)
        for i in range(no_of_chuncks):
            coefficient = np.polyfit(self.x_scattered_points[i * intervals:intervals * (i + 1) - 1],
                                     self.y_scattered_points[0 + i * intervals:intervals * (i + 1) - 1], function_degree)
            coefficient_list.append(coefficient)

    def interpolation(self):
        print("inside interpolation")
        self.function_degree = self.polynomial_degree_slider.value()
        self.no_of_chuncks = self.number_of_chunks_slider.value()
        coefficient_list = self.fitting_datd(self.function_degree, self.no_of_chuncks)
        print("after interpolation")

        xfit = np.linspace(0, self.x_scattered_points[-1], 1000)
        yfit = []
        x_cunk_boundry = []
        intervals = int(len(xfit) /self.no_of_chuncks)

        for i in range(self.no_of_chuncks):
            xchunk = xfit[i * intervals:intervals * (i + 1) - 1]
            chunk_fit = np.poly1d(coefficient_list[i])
            yfit.extend(chunk_fit(xchunk))
            x_cunk_boundry.append(xchunk[-1])
            tt = intervals * (i + 1) - 1
            # if(i == no_of_chuncks and intervals * (i + 1)<len(xfit)-1 ):
            #     xchunk = xfit[(i+1) * intervals:]
            #     yfit.extend(chunk_fit(xchunk))
            #     x_cunk_boundry.append(xchunk[-1])
        if (len(yfit) < len(xfit)):
            lastx_chunk = xfit[len(yfit):]
            last_chunk_fit = np.poly1d(coefficient_list[-1])
            yfit.extend(last_chunk_fit(lastx_chunk))
        self.canves.axes.plot(xfit,yfit)
        self.canves.axes.plot(self.x_scattered_points,self.y_scattered_points,"-o")
        self.canves.draw()

    def toggleStartCancel(self):
        curr_text = self.error_map_button.text()
        if curr_text == "Start":
            self.error_map_button.setText("Cancel")
            self.error_map_button.setStyleSheet("background-color: #930000;")
        else:
            self.error_map_button.setText("Start")
            self.error_map_button.setStyleSheet("background-color: rgb(0, 54, 125);")

    def error_map_handler(self):
        curr_text = self.error_map_button.text()
        if curr_text == "Start":
            if not self.thread_error_map.is_running:
                self.thread_error_map.start()
                self.toggleStartCancel()

        if curr_text == "Cancel":
            if self.thread_error_map.is_running:
                self.thread_error_map.stop()
                self.progressBar.setValue(0)
                self.toggleStartCancel()

    def update_progressbar(self,val):
        self.progressBar.setValue(val)
        self.thread_error_map.start()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Main_window()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

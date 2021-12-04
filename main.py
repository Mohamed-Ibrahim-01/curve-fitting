import matplotlib as matplotlib
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets, uic
import qdarkstyle

matplotlib.use('Qt5Agg')
from matplotlib.pyplot import isinteractive
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from ErrorMap import ErrorMap, ThreadedErrorMap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
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
        uic.loadUi('gui_main.ui', self)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # Menu Bar
        self.menubar = self.findChild(QtWidgets.QMenuBar, "menubar")
        self.menuFile = self.menubar.findChild(QtWidgets.QMenu, "menuFile")
        print(type(self.menuFile))
        self.menuFile.addAction("open", self.open_file)
        #   =self.menuFile.findChild(QtWidgets.QAction,"actionoppppen")
        # print(type(self.openAction))

        # graph layout
        self.error_map = ErrorMap()
        self.erro_map_layout.insertWidget(0, self.error_map)

        # Radio_butto_Layout
        # radio buttons
        self.one_chunk_button = self.findChild(QtWidgets.QRadioButton, "one_chunk")
        self.multiple_chunks_button = self.findChild(QtWidgets.QRadioButton, "mlutiple_chunks")

        # grid layout
        # sliders
        self.data_percentage_slider = self.findChild(QtWidgets.QSlider, "data_percentage_slider")
        self.number_of_chunks_slider = self.findChild(QtWidgets.QSlider, "number_of_chunks_slider")
        self.polynomial_degree_slider = self.findChild(QtWidgets.QSlider, "polynomial_degree_slider")
        self.number_of_chunks_slider.setValue(1)
        self.sliders_arr = [self.data_percentage_slider, self.number_of_chunks_slider, self.polynomial_degree_slider]

        # lables
        self.data_percentage_label = self.findChild(QtWidgets.QLabel, "data_percentage_label")
        self.number_of_chunks_lable = self.findChild(QtWidgets.QLabel, "number_of_chunks_lable")
        self.degree_lable = self.findChild(QtWidgets.QLabel, "degree_lable")
        self.lables_arr = [self.data_percentage_label, self.number_of_chunks_lable,
                           self.degree_lable]
        self.lable_3 = self.findChild(QtWidgets.QLabel, "label_3")
        self.eq_lable =  self.findChild(QtWidgets.QLabel,"eq_label")
        #Buttons
        self.ploting_button = self.findChild(QtWidgets.QPushButton,"start_button")
        self.plotting_flag = True
        self.fitting_button = self.findChild(QtWidgets.QPushButton,"fitting_button")

        # combo Box
        self.poly_eq_box = self.findChild(QtWidgets.QComboBox,"poly_eq_box")

        # canves widget
        self.canves = MplCanvas()
        self.graph_layout.addWidget(self.canves)

        # init:
        self.init_visability_with_radio_buttons()

        # signals
        #   radio button(multiple)
        self.multiple_chunks_button.toggled.connect(self.setting_chunks_mode)
        #   signal func arr
        self.signals_func_arr = [lambda value, i=0: self.slider_updated(value, i),
                                 lambda value, i=1: self.slider_updated(value, i),
                                 lambda value, i=2: self.slider_updated(value, i)]

        for i in range(len(self.sliders_arr)):
            self.sliders_arr[i].valueChanged.connect(self.signals_func_arr[i])

        # Plot buttons signal
        self.ploting_button.clicked.connect(self.plot_data)
        self.fitting_button.clicked.connect(self.interpolation)
        self.error_map_button.clicked.connect(self.error_map_handler)
        self.error_map.ready.connect(self.toggleStartCancel)

        self.threaded_error_map = ThreadedErrorMap(self.getError)
        self.threaded_error_map.currProgress.connect(self.update_progressbar)
        self.threaded_error_map.ready.connect(self.showErrorMap)

        # combo box signals

        self.poly_eq_box.activated.connect(self.poly_eq_box_selected)
        # self.openAction.triggered.connect(self.open_file())

        # Data

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

    def slider_updated(self, value, i):
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
            self.canves.axes.plot(self.x_scattered_points, self.y_scattered_points, "o", markersize=2)
            self.canves.draw()
            self.plotting_flag = False
            self.ploting_button.setText("Clear Scatterd Points")
        else:
            self.canves.axes.cla()
            self.canves.axes.grid()
            self.canves.draw()
            self.plotting_flag = True
            self.ploting_button.setText("Plot Scatterd Points")

    def getError(self, function_degree, no_of_chuncks):
        "Hello Guys"
        total_Residual = 0
        length_of_data = len(self.x_scattered_points)
        intervals = int(length_of_data / no_of_chuncks)
        for i in range(no_of_chuncks):
            coefficients, residual, *_ = np.polyfit(self.x_scattered_points[i * intervals:intervals * (i + 1) - 1],
                                                    self.y_scattered_points[
                                                    0 + i * intervals:intervals * (i + 1) - 1],
                                                    function_degree, full=True)
            if len(residual) > 0:
                total_Residual = total_Residual + residual[0]
        return total_Residual

    def fitting_data(self, function_degree, no_of_chuncks):
        print("iside fiiting1")
        self.poly_box_adjustment()
        coefficient_list = []
        length_of_data = len(self.x_scattered_points)

        intervals = length_of_data // no_of_chuncks

        for i in range(no_of_chuncks):
            coefficient = np.polyfit(self.x_scattered_points[i * intervals:intervals * (i + 1) - 1],
                                     self.y_scattered_points[0 + i * intervals:intervals * (i + 1) - 1],
                                     function_degree)
            coefficient_list.append(coefficient)
        return coefficient_list

    def interpolation(self):
        print("inside interpolation")
        print(self.polynomial_degree_slider.value())

        self.degree = self.polynomial_degree_slider.value()
        self.no_of_chuncks = self.number_of_chunks_slider.value()
        print("after slider")
        self.coefficient_list = self.fitting_data(self.degree, self.no_of_chuncks)
        print("after interpolation")

        xfit = np.linspace(0, self.x_scattered_points[-1], 1000)
        yfit = []
        x_cunk_boundry = []
        intervals = int(len(xfit) / self.no_of_chuncks)

        for i in range(self.no_of_chuncks):
            xchunk = xfit[i * intervals:intervals * (i + 1) - 1]
            chunk_fit = np.poly1d(self.coefficient_list[i])
            chunk_fit = chunk_fit(xchunk)
            chunk_fit[0:5] = 0
            yfit.extend(chunk_fit)
            x_cunk_boundry.append(xchunk[-1])
            tt = intervals * (i + 1) - 1
            # if(i == no_of_chuncks and intervals * (i + 1)<len(xfit)-1 ):
            #     xchunk = xfit[(i+1) * intervals:]
            #     yfit.extend(chunk_fit(xchunk))
            #     x_cunk_boundry.append(xchunk[-1])
        if (len(yfit) < len(xfit)):
            lastx_chunk = xfit[len(yfit):]
            last_chunk_fit = np.poly1d(self.coefficient_list[-1])
            yfit.extend(last_chunk_fit(lastx_chunk))
        print("after interpolation befor plotting")
        # max = max(self.y_scattered_points)
        # min = min(self.y_scattered_points)
        for i in range(len(yfit)):
            if yfit[i] > max(self.y_scattered_points) or yfit[i] < min(self.y_scattered_points):
                yfit[i] = 0
        # print("coeeeeff ",self.coefficient_list )
        # polynomial_formela = self.print_poly(self.coefficient_list[0])


        # self.canves.axes.set_xlim(0,max(self.x_scattered_points))
        self.canves.axes.plot(xfit,yfit,"--")
        self.canves.axes.legend(loc='upper right')
        self.canves.axes.set_xlim(0,max(self.x_scattered_points))
        self.canves.draw()

    def toggleStartCancel(self):
        curr_text = self.error_map_button.text()
        print(f"I'am {curr_text}")
        if curr_text == "Start":
            self.error_map_button.setText("Cancel")
            self.error_map_button.setStyleSheet("background-color: #930000;")
        else:
            self.error_map_button.setText("Start")
            self.error_map_button.setStyleSheet("background-color: rgb(0, 54, 125);")

    def error_map_handler(self):

        curr_text = self.error_map_button.text()
        if curr_text == "Start":
            if not self.threaded_error_map.is_running:
                self.threaded_error_map.start()
                self.toggleStartCancel()

        if curr_text == "Cancel":
            if self.threaded_error_map.is_running:
                self.threaded_error_map.stop()
                self.progressBar.setValue(0)
                self.toggleStartCancel()

    def update_progressbar(self, val):
        self.progressBar.setValue(val)
        self.threaded_error_map.start()

    def showErrorMap(self, error_map_data):
        self.error_map.plotErrorMap(error_map_data)


    def print_poly(self,list):
        polynomial = ''
        order = len(list) - 1
        for coef in list:
            if coef is not 0 and order is 1:
                term = str(coef) + 'x'
                polynomial += term
            elif coef is not 0 and order is 0:
                term = str(coef)
                polynomial += term
            elif coef is not 0 and order is not 0 and order is not 1:
                term = str(coef) + 'x^' + str(order)
                polynomial += term
            elif coef is 0:
                pass

            if order is not 0 and coef is not 0:
                polynomial += ' + '
            order += -1
        # print(polynomial)
        return polynomial

    def poly_box_adjustment(self):
        for i in range(self.no_of_chuncks):
            self.poly_eq_box.addItem("Chunk : "+str(i+1))


    def poly_eq_box_selected(self,index):
        selected_eq_coefficients = self.coefficient_list[index]
        self.polynomial_eq = self.print_poly(np.round(selected_eq_coefficients,2))

        self.eq_lable.setText(self.polynomial_eq)





def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Main_window()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

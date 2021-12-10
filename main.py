import matplotlib as matplotlib
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets, uic
import PyQt5.QtCore as qtc
import qdarkstyle
from sklearn.utils import shuffle
from matplotlib import pyplot as plt

matplotlib.use('Qt5Agg')
from matplotlib.pyplot import isinteractive
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from ErrorMap import ErrorMap, ErrorMapWorker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=0.1, height=0.01, dpi=100):
        self.fig =Figure()
        self.axes = self.fig.add_subplot(111)
        for spine in ['right', 'top', 'left', 'bottom']:
            self.axes.spines[spine].set_color('gray')
        self.axes.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        super().__init__(self.fig)
        self.fig.tight_layout()

class latex_canves(FigureCanvas):

    def __init__(self, parent=None, width=0, height=0, dpi=150):
        self.fig2 = Figure(figsize=(width, height), dpi=dpi)
        self.axes2 = self.fig2.add_subplot(111)
        for spine in ['right', 'top', 'left', 'bottom']:
            self.axes2.spines[spine].set_visible(False)
        self.axes2.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        super().__init__(self.fig2)

class Main_window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main_window, self).__init__()
        uic.loadUi('gui_main.ui', self)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # Menu Bar
        self.menubar = self.findChild(QtWidgets.QMenuBar, "menubar")
        self.menuFile = self.menubar.findChild(QtWidgets.QMenu, "menuFile")
        self.menuFile.addAction("open", self.open_file)
        #   =self.menuFile.findChild(QtWidgets.QAction,"actionoppppen")
        # print(type(self.openAction))

        # graph layout
        self.error_map = ErrorMap()
        self.erro_map_layout.insertWidget(0, self.error_map)
        self.x_axis = "Number of Chunks"
        self.y_axis = "Polynomial Degree"


        # Radio_butto_Layout
        # radio buttons
        self.polydeg = self.findChild(QtWidgets.QRadioButton, "polydeg")
        self.numchunk = self.findChild(QtWidgets.QRadioButton, "numchunk")
        self.one_chunk_button = self.findChild(QtWidgets.QRadioButton, "one_chunk")
        self.multiple_chunks_button = self.findChild(QtWidgets.QRadioButton, "mlutiple_chunks")

        # grid layout
        # sliders
        self.data_percentage_slider = self.findChild(QtWidgets.QSlider, "data_percentage_slider")
        self.number_of_chunks_slider = self.findChild(QtWidgets.QSlider, "number_of_chunks_slider")
        self.polynomial_degree_slider = self.findChild(QtWidgets.QSlider, "polynomial_degree_slider")
        self.number_of_chunks_slider.setValue(1)

        self.data_percentage_slider.setValue(100)

        self.sliders_arr = [self.data_percentage_slider, self.number_of_chunks_slider,self.polynomial_degree_slider]


        self.sliders_arr = [self.data_percentage_slider, self.number_of_chunks_slider, self.polynomial_degree_slider]
        # lables
        self.data_percentage_label = self.findChild(QtWidgets.QLabel, "data_percentage_label")
        self.data_percentage_label.setText(str(100))
        self.number_of_chunks_lable = self.findChild(QtWidgets.QLabel, "number_of_chunks_lable")
        self.number_of_chunks_lable.setText(str(1))

        self.degree_lable = self.findChild(QtWidgets.QLabel, "degree_lable")

        self.lables_arr = [self.data_percentage_label, self.number_of_chunks_lable,
                           self.degree_lable]
        self.lable_3 = self.findChild(QtWidgets.QLabel, "label_3")
        # self.eq_lable =  self.findChild(QtWidgets.QLabel,"eq_label")
        #Buttons
        self.ploting_button = self.findChild(QtWidgets.QPushButton,"start_button")
        self.plotting_flag = True
        self.fitting_button = self.findChild(QtWidgets.QPushButton,"fitting_button")

        # combo Box
        self.poly_eq_box = self.findChild(QtWidgets.QComboBox,"poly_eq_box")
        self.overlap = self.findChild(QtWidgets.QSpinBox, "overlap")

        # canves widget
        self.canves = MplCanvas()
        self.graph_layout.addWidget(self.canves)
        self.current_fitted_line,  = self.canves.axes.plot([],[])

        # Latex widget
        self.latex_widget = latex_canves()
        self.latex_layout = self.findChild(QtWidgets.QHBoxLayout,"latex_layout")
        # self.latex_layout.set
        self.latex_layout.addWidget(self.latex_widget)

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

        self.data_percentage_slider.valueChanged.connect(self.change_percentage_of_fitted_data)
        # Plot buttons signal
        self.ploting_button.clicked.connect(self.plot_data)
        self.fitting_button.clicked.connect(self.interpolation)
        self.error_map_button.clicked.connect(self.error_map_handler)


        # combo box signals

        self.poly_eq_box.activated.connect(self.poly_eq_box_selected)
        # self.openAction.triggered.connect(self.open_file())

        # Data

        self.polydeg.toggled.connect(self.change_axis)
    def change_axis(self):
        if self.polydeg.isChecked():
            self.x_axis = "Polynomial Degree"
            self.y_axis = "Number of Chunks"
        else:
            self.y_axis = "Polynomial Degree"
            self.x_axis = "Number of Chunks"

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

            self.max_xlim_point = max( self.x_scattered_points)
            self.min_xlim_point = min( self.x_scattered_points)

    def plot_data(self):
        if self.plotting_flag:
            self.scatterd_points, = self.canves.axes.plot(self.x_scattered_points, self.y_scattered_points, "o", markersize=2)
            self.canves.draw()
            self.plotting_flag = False
            self.ploting_button.setText("Clear Scatterd Points")
        else:
            # self.canves.axes.cla()
            self.scatterd_points.remove()
            # self.canves.axes.grid()
            self.canves.draw()
            self.plotting_flag = True
            self.ploting_button.setText("Plot Scatterd Points")

    def getErrorOverlap(self, function_degree,no_of_chuncks,overlapping):
        total_Residual = 0
        length_of_data = len(self.x_scattered_points)
        intervals = int(length_of_data / no_of_chuncks)
        for i in range(no_of_chuncks):
            if i == 0:
                coefficients, residual, _, _, _  = np.polyfit(self.x_scattered_points[i*intervals:intervals*(i+1)-1],self.y_scattered_points[0+i*intervals:intervals*(i+1)-1],function_degree,full='true')
                if len(residual) > 0:
                    total_Residual = total_Residual + residual[0]

            elif i<no_of_chuncks-1:
                coefficients, residual, _, _, _  = np.polyfit(self.x_scattered_points[i*intervals-int(i*intervals*(overlapping/100)):intervals*(i+1)-1-int(i*intervals*(overlapping/100))]
                ,self.y_scattered_points[i*intervals-int(i*intervals*(overlapping/100)):intervals*(i+1)-1-int(i*intervals*(overlapping/100))],function_degree,full='true')
                if len(residual) > 0:
                    total_Residual = total_Residual + residual[0]

            else:
                coefficients, residual, _, _, _  = np.polyfit(self.x_scattered_points[intervals*(i)-1-int((i-1)*intervals*(overlapping/100)):length_of_data]
                ,self.y_scattered_points[intervals*(i)-1-int((i-1)*intervals*(overlapping/100)):length_of_data],function_degree,full='true')
                if len(residual) > 0:
                    total_Residual = total_Residual + residual[0]
        return total_Residual/np.sqrt(length_of_data)

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

    def fitting_data(self, function_degree, no_of_chunks):
        NUM_OF_POINTS = 1000

        num_of_points_for_intervals = NUM_OF_POINTS // no_of_chunks

        chunks_list_x = np.array_split(self.x_scattered_points, no_of_chunks)
        chunks_list_y = np.array_split(self.y_scattered_points, no_of_chunks)

        y_fit_list = []
        x_fit_list = []
        for i in range(no_of_chunks):
            chunk_coeff = np.polyfit(chunks_list_x[i], chunks_list_y[i], function_degree)
            chunk_modles = np.poly1d(chunk_coeff)
            print(str(chunk_modles))
            x_fit = np.linspace(chunks_list_x[i][0], chunks_list_x[i][-1], num_of_points_for_intervals)
            x_fit_list.extend(x_fit)

            y_fit = chunk_modles(x_fit)
            y_fit_list.extend(y_fit)

        return x_fit_list, y_fit_list

    def interpolation(self):
        self.latex_widget.axes2.cla()
        self.latex_widget.draw()
        print("inside interpolation")
        print(self.polynomial_degree_slider.value())

        self.degree = self.polynomial_degree_slider.value()
        self.no_of_chuncks = self.number_of_chunks_slider.value()
        print("after slider")
        xfit , yfit = self.fitting_data(self.degree, self.no_of_chuncks)
        print("after interpolation")


        print("befor setdata")
        self.current_fitted_line.set_data(xfit,yfit)
        print("after setdata")

        self.canves.axes.set_xlim(self.min_xlim_point,self.max_xlim_point)
        # self.canves.axes.grid()
        self.canves.draw()

    def setStartButton(self):
        self.error_map_button.setText("Start")
        self.error_map_button.setStyleSheet("background-color: rgb(0, 54, 125);")

    def setCancelButton(self):
        self.error_map_button.setText("Cancel")
        self.error_map_button.setStyleSheet("background-color: #930000;")

    def toggleStartCancel(self):
        curr_text = self.error_map_button.text()
        if curr_text == "Start": self.setCancelButton()
        else: self.setStartButton()

    def error_map_handler(self):

        curr_text = self.error_map_button.text()
        if curr_text == "Start":
            overlap_value = self.overlap.value()
            self.error_map_worker = ErrorMapWorker(self.getErrorOverlap, overlap_value)
            self.error_map_thread = qtc.QThread()
            self.error_map_worker.currProgress.connect(self.update_progressbar)
            self.error_map_worker.moveToThread(self.error_map_thread)
            self.error_map_worker.ready.connect(self.showErrorMap)
            self.error_map_thread.started.connect(self.error_map_worker.run)
            self.error_map_thread.start()
            self.setCancelButton()

        if curr_text == "Cancel":
            self.error_map_worker.stop()
            self.setStartButton()
            self.error_map.clear()

    def update_progressbar(self, val):
        self.progressBar.setValue(val)

    def showErrorMap(self,canceled, error_map_data):
        self.error_map_thread.quit()
        if not canceled :
            self.error_map_plot = self.error_map.plotErrorMap(
                error_map_data, x_axis=self.x_axis, y_axis=self.y_axis
            )
        self.setStartButton()
        self.progressBar.setValue(0)


    def print_poly(self,list):
        polynomial = ''
        order = len(list) - 1
        for coef in list:
            if coef != 0 and order == 1:
                term = str(coef) + 'x'
                polynomial += term
            elif coef != 0 and order == 0:
                term = str(coef)
                polynomial += term
            elif coef != 0 and order != 0 and order != 1:
                term = str(coef) + 'x^' + str(order)
                polynomial += term
            elif coef == 0:
                pass

            if order != 0 and coef != 0:
                polynomial += ' + '
            order += -1
        # print(polynomial)
        return polynomial

    def poly_box_adjustment(self):
        self.poly_eq_box.clear()
        for i in range(self.no_of_chuncks):
            self.poly_eq_box.addItem("Chunk : "+str(i+1))


    def poly_eq_box_selected(self,index):
        selected_eq_coefficients = self.coefficient_list[index]
        self.polynomial_eq = self.print_poly(np.round(selected_eq_coefficients,2))

        self.latex_widget.axes2.cla()
        self.latex_widget.draw()
        self.latex_widget.axes2.text(0, 5, "$"+self.polynomial_eq+"$")
        self.latex_widget.axes2.axis([0, 10, 0, 10])
        self.latex_widget.draw()

    def change_percentage_of_fitted_data(self,value):
        self.x_scattered_points = self.loaded_data[self.loaded_data.columns[0]].to_numpy()
        self.y_scattered_points = self.loaded_data[self.loaded_data.columns[1]].to_numpy()
        lenth = len(self.x_scattered_points)
        last_idx = int(lenth*(value/100)) -1
        print("percentage of data error")
        self.x_scattered_points = self.x_scattered_points[0:last_idx]
        self.y_scattered_points = self.y_scattered_points[0:last_idx]




def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Main_window()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

import sys
import pandas as pd
import numpy as np
import qdarkstyle
import Error
import matplotlib as matplotlib
from PyQt5 import QtWidgets, uic
from sklearn.utils import shuffle

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from ErrorMap import ErrorMap, ErrorMapWorker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as navigation_toolbar

from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=0.1, height=0.01, dpi=100):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        for spine in ['right', 'top', 'left', 'bottom']:
            self.axes.spines[spine].set_color('gray')
        # self.axes.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
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
        self.error_map = ErrorMap(self.getErrorOverlap)
        self.splitter.findChild(QtWidgets.QVBoxLayout, "error_map_area")
        self.error_map_area.addWidget(self.error_map)

        # Radio_butto_Layout
        # radio buttons

        self.one_chunk_button = self.findChild(QtWidgets.QRadioButton, "one_chunk")
        self.multiple_chunks_button = self.findChild(QtWidgets.QRadioButton, "mlutiple_chunks")
        self.one_chunk_button.setChecked(True)


        # grid layout
        # sliders
        self.data_percentage_slider = self.findChild(QtWidgets.QSlider, "data_percentage_slider")
        self.number_of_chunks_slider = self.findChild(QtWidgets.QSlider, "number_of_chunks_slider")
        self.polynomial_degree_slider = self.findChild(QtWidgets.QSlider, "polynomial_degree_slider")
        self.number_of_chunks_slider.setValue(1)

        self.data_percentage_slider.setValue(100)

        self.sliders_arr = [self.data_percentage_slider, self.number_of_chunks_slider, self.polynomial_degree_slider]

        # self.sliders_arr = [self.data_percentage_slider, self.number_of_chunks_slider, self.polynomial_degree_slider]
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
        # Buttons
        self.ploting_button = self.findChild(QtWidgets.QPushButton, "start_button")
        self.plotting_flag = True

        # combo Box
        self.poly_eq_box = self.findChild(QtWidgets.QComboBox, "poly_eq_box")

        # canves widget
        self.canves = MplCanvas()
        self.graph_layout.addWidget(self.canves)
        self.current_fitted_line, = self.canves.axes.plot([], [], '--')

        # Latex widget

        self.latex_widget = latex_canves()
        self.toolbar = navigation_toolbar(self.latex_widget, self)

        self.equations_layout = self.findChild(QtWidgets.QVBoxLayout, "equations_layout")
        self.latex_canves_layout = self.equations_layout.findChild(QtWidgets.QVBoxLayout, "latex_layout")
        self.toolbar_layout = self.equations_layout.findChild(QtWidgets.QHBoxLayout, "toolbar_layout")

        self.latex_canves_layout.addWidget(self.latex_widget)
        self.toolbar_layout.addWidget(self.toolbar)




        self.signals_lables_arr = [lambda value, i=0: self.slider_updated(value, i),
                                 lambda value, i=1: self.slider_updated(value, i),
                                 lambda value, i=2: self.slider_updated(value, i)]

        self.signals_interpolation_arr = [lambda : self.interpolation(),
                                 lambda : self.interpolation(),
                                 lambda : self.interpolation()]

        # if self.one_chunk_button.isChecked():
        #     self.signals_interpolation_arr[0] = lambda value : self.change_percentage_of_fitted_data(value)
        #     # self.percentage = self.data_percentage_slider
        #     self.signals_interpolation_arr[2] = lambda x , percentage =self.data_percentage_slider.value()  : self.change_percentage_of_fitted_data(percentage)




        self.data_percentage_slider.valueChanged.connect(self.change_percentage_of_fitted_data)
        self.ploting_button.clicked.connect(self.plot_data)
        self.poly_eq_box.activated.connect(self.poly_eq_box_selected)


        self.init_visibility_with_radio_buttons()
        self.multiple_chunks_button.toggled.connect(self.setting_chunks_mode)

        for i in range(len(self.sliders_arr)):
            self.sliders_arr[i].valueChanged.connect(self.signals_lables_arr[i])

        # for i in range(len(self.sliders_arr)):
        #     self.sliders_arr[i].valueChanged.connect(self.signals_interpolation_arr[i])
        #     print(self.signals_interpolation_arr[i])

        self.sliders_arr[0].valueChanged.connect(self.signals_interpolation_arr[0])
        self.sliders_arr[1].valueChanged.connect(self.signals_interpolation_arr[1])
        self.sliders_arr[2].valueChanged.connect(self.signals_interpolation_arr[2])

        # self.multiple_chunks_button.toggled.connect(self.setting_chunks_mode)

    def init_visibility_with_radio_buttons(self):
        self.setting_chunks_mode()

    def setting_chunks_mode(self):
        if self.multiple_chunks_button.isChecked():
            self.number_of_chunks_slider.show()
            self.lable_3.show()
            self.number_of_chunks_lable.show()
            self.data_percentage_slider.setValue(100)
            # self.data_percentage_slider.hide()
            self.signals_interpolation_arr[0] = lambda x: self.interpolation()
            self.signals_interpolation_arr[2] =  lambda x: self.interpolation()
            self.polynomial_degree_slider.valueChanged.connect(self.interpolation)

            print(self.signals_interpolation_arr)

            print("inside multible of chunks sttings")
        else:
            self.data_percentage_slider.show()
            self.number_of_chunks_slider.hide()
            self.lable_3.hide()
            self.number_of_chunks_lable.hide()
            self.number_of_chunks_slider.setValue(1)

            self.signals_interpolation_arr[0] = lambda value : self.change_percentage_of_fitted_data(value)
            self.signals_interpolation_arr[2] = lambda value : self.change_percentage_of_fitted_data(value)
            self.polynomial_degree_slider.valueChanged.connect(self.change_percentage_of_fitted_data)

            print("inside one of chunks sttings")

            print(self.signals_interpolation_arr)




    def slider_updated(self, value, i):
        self.lables_arr[i].setText(str(value))

    def open_file(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName()
        if filename:
            self.loaded_data = pd.read_csv(filename)
            self.x_scattered_points = self.loaded_data[self.loaded_data.columns[0]].to_numpy()
            self.y_scattered_points = self.loaded_data[self.loaded_data.columns[1]].to_numpy()

            self.max_xlim_point = max(self.x_scattered_points)
            self.min_xlim_point = min(self.x_scattered_points)
            self.plotting_flag = True
            self.canves.axes.set_xlim(self.min_xlim_point, self.max_xlim_point)
            self.plot_data()

    def plot_data(self):
        if self.plotting_flag:
            self.scatterd_points, = self.canves.axes.plot(self.x_scattered_points, self.y_scattered_points,"-",
                                                          markersize=2)
            self.canves.draw()
            self.plotting_flag = False
            self.ploting_button.setText("Clear Original Signal")
        else:
            # self.canves.axes.cla()
            self.scatterd_points.remove()
            # self.canves.axes.grid()
            self.canves.draw()
            self.plotting_flag = True
            self.ploting_button.setText("Plot Original Signal")

    def getErrorOverlap(self, degree, num_of_chunks, overlap):
        return Error.getError(
            degree, num_of_chunks, overlap, self.x_scattered_points, self.y_scattered_points
        )

    def getError(self, degree, num_of_chunks):
        return Error.getError(
            degree, num_of_chunks, 0, self.x_scattered_points, self.y_scattered_points
        )

    def fitting_data(self, function_degree, no_of_chunks):
        NUM_OF_POINTS = 1000
        self.poly_box_adjustment()
        num_of_points_for_intervals = NUM_OF_POINTS // no_of_chunks

        chunks_list_x = np.array_split(self.x_scattered_points, no_of_chunks)
        chunks_list_y = np.array_split(self.y_scattered_points, no_of_chunks)
        self.coeff_chunks_list = []
        y_fit_list = []
        x_fit_list = []
        for i in range(no_of_chunks):
            chunk_coeff = np.polyfit(chunks_list_x[i], chunks_list_y[i], function_degree)
            self.coeff_chunks_list.append(chunk_coeff)
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
        xfit, yfit = self.fitting_data(self.degree, self.no_of_chuncks)
        print("after interpolation")
        # gitting error
        abs_error = self.getError(self.degree, self.no_of_chuncks)
        base_error = self.getError(0, 1)
        self.percentage_error = 100 * np.round(abs_error / base_error, 2)

        print("befor setdata")
        self.current_fitted_line.set_data(xfit, yfit)
        print("after setdata")
        self.current_fitted_line.set_label("Percentage Error: " + str(self.percentage_error) + " %")

        self.canves.axes.set_xlim(self.min_xlim_point, self.max_xlim_point)
        # self.canves.axes.grid()
        self.canves.axes.legend()
        self.canves.draw()

    def print_poly(self, list):
        polynomial = ''
        order = len(list) - 1
        for coef in list:
            if coef != 0 and order == 1:
                term = str(coef) + 'X'
                polynomial += term
            elif coef != 0 and order == 0:
                term = str(coef)
                polynomial += term
            elif coef != 0 and order != 0 and order != 1:
                term = str(coef) + 'X^' + "{" + str(order) + "}"
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
            self.poly_eq_box.addItem("Chunk : " + str(i + 1))

    def poly_box_adjustment_extrapolation(self):
        self.poly_eq_box.clear()

        self.poly_eq_box.addItem("Chunk : " + str(1))

    def poly_eq_box_selected(self, index=1):
        # selected_eq_coefficients = self.coefficient_list[index]
        selected_eq_coefficients = self.coeff_chunks_list[index]
        self.polynomial_eq = self.print_poly(np.round(selected_eq_coefficients, 2))

        self.latex_widget.axes2.cla()
        self.latex_widget.draw()
        self.latex_widget.axes2.text(0, 5, "$" + self.polynomial_eq + "$")
        self.latex_widget.axes2.axis([0, 10, 0, 10])
        self.latex_widget.draw()

    def change_percentage_of_fitted_data(self, value):
        self.x_scattered_points = self.loaded_data[self.loaded_data.columns[0]].to_numpy()
        self.y_scattered_points = self.loaded_data[self.loaded_data.columns[1]].to_numpy()
        lenth = len(self.x_scattered_points)
        value = self.data_percentage_slider.value()
        last_idx = int(lenth * (value / 100)) - 1
        print("percentage of data error")

        x_clipped = self.x_scattered_points[0:last_idx]
        y_clipped = self.y_scattered_points[0:last_idx]

        self.x_scattered_points = x_clipped
        self.y_scattered_points = y_clipped
        # self.one_chunk_button.setChecked(True)
        # self.number_of_chunks_slider.setValue(1)

        self.scatterd_points.set_data(x_clipped,y_clipped)
        self.canves.draw()
        self.extrapolation()

    def fitting(self, degree):
        NUM_OF_POINTS = 1000
        no_fo_chunks = 1
        x_fit = np.linspace(self.min_xlim_point, self.max_xlim_point, NUM_OF_POINTS)

        chunks_list_x = np.array_split(self.x_scattered_points , no_fo_chunks)
        chunks_list_y = np.array_split(self.y_scattered_points, no_fo_chunks)

        x_fit_chunks_list = np.array_split(x_fit, no_fo_chunks)

        y_fit_list = []
        self.coeff_chunks_list = []
        self.poly_box_adjustment_extrapolation()
        for i in range(no_fo_chunks):
            chunk_coeff = np.polyfit(chunks_list_x[i], chunks_list_y[i], degree)
            self.coeff_chunks_list.append(chunk_coeff)
            chunk_modles = np.poly1d(chunk_coeff)

            y_fit = chunk_modles(x_fit_chunks_list[i])

            y_fit_list.extend(y_fit)

        return x_fit, y_fit_list

    def extrapolation(self):
        poly_degree = self.polynomial_degree_slider.value()
        x_extrapolation, y_extrapolation = self.fitting(poly_degree)
        self.current_fitted_line.set_data(x_extrapolation,y_extrapolation)

        degree = self.polynomial_degree_slider.value()
        abs_error = self.getError(degree, 1)
        base_error = self.getError(0, 1)
        self.percentage_error = 100 * np.round(abs_error / base_error, 2)
        self.current_fitted_line.set_label("Percentage Error: " + str(self.percentage_error) + " %")
        self.canves.axes.legend()

        self.canves.draw()


    def change_percentage_of_fitted_data_with_shuffling(self, value):
        self.x_scattered_points = self.loaded_data[self.loaded_data.columns[0]].to_numpy()
        self.y_scattered_points = self.loaded_data[self.loaded_data.columns[1]].to_numpy()
        lenth = len(self.x_scattered_points)

        last_idx = int(lenth * (value / 100)) - 1
        print("percentage of data error")


        x_shuffled, y_shuffled = shuffle(self.x_scattered_points, self.y_scattered_points)

        x_shuffled = np.array(x_shuffled[0:last_idx])
        y_shuffled = np.array(y_shuffled[0:last_idx])

        sorted_idx = x_shuffled.argsort()

        x_shuffled = x_shuffled[sorted_idx]
        y_shuffled = y_shuffled[sorted_idx]

        self.x_scattered_points = x_shuffled
        self.y_scattered_points = y_shuffled


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Main_window()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

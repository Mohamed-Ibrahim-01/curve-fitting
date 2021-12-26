import random
import numpy as np
import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import constants as cst

from PyQt5 import uic
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.style.use('dark_background')


def randomErrorCalculation(*args, **kwargs):
    return random.uniform(0, 1)


def getCheckedRadioButton(radio_btns):
    for rb in radio_btns:
        if rb.isChecked():
            return rb.text()


class ErrorMap(qtw.QWidget):
    ready = qtc.pyqtSignal()
    progressChanged = qtc.pyqtSignal(int)

    def __init__(self, calc_error):
        super().__init__()
        uic.loadUi('error_map.ui', self)

        self.error_map_plot = None
        self.error_map_thread = None
        self.error_map_worker = None
        self.error_map_x_axis_text = cst.NUMBER_OF_CHUNKS
        self.error_map_y_axis_text = cst.POLYNOMIAL_DEGREE
        self.error_map_z_axis_text = cst.OVERLAP
        self.x_axis_range = np.arange(30)+1
        self.y_axis_range = np.arange(30)+1
        self.calc_error = calc_error
        self.cleared = True

        self.canvas = ErrorMapCanvas()
        self.layout().insertWidget(0, self.canvas)
        self.error_map_x_axis = self.findChild(qtw.QGroupBox, "x_axis_groupBox")
        self.error_map_y_axis = self.findChild(qtw.QGroupBox, "y_axis_groupBox")
        self.error_map_z_axis = self.findChild(qtw.QGroupBox, "z_axis_layout")
        self.z_axis_spinbox = self.findChild(qtw.QSpinBox, "z_axis_spinbox")
        self.color_map_combo = self.findChild(qtw.QComboBox, "color_map")

        self.error_map_x_axis_radio_btns = self.error_map_x_axis.findChildren(qtw.QRadioButton)
        self.error_map_y_axis_radio_btns = self.error_map_y_axis.findChildren(qtw.QRadioButton)

        self.error_map_radio_btns = self.error_map_x_axis_radio_btns.copy()
        self.error_map_radio_btns.extend(self.error_map_y_axis_radio_btns)

        self.error_map_button.clicked.connect(self.errorMapHandler)
        self.color_map_combo.currentIndexChanged.connect(self.updatePalate)
        for radio_btn in self.error_map_radio_btns:
            radio_btn.toggled.connect(self._changeAxis)

    def updatePalate(self):
        curr_palate = self.color_map_combo.currentText()
        if not self.cleared:
            self.error_map_plot.set_cmap(curr_palate)
            self.canvas.color_bar.mappable.set_cmap(curr_palate)
            self.canvas.draw()

    def showErrorMap(self, canceled, error_map_data):
        self.error_map_thread.quit()
        color_map = self.color_map_combo.currentText()
        if not canceled:
            self.error_map_plot = self.canvas.plot(
                error_map_data,
                x_axis=self.error_map_x_axis_text,
                y_axis=self.error_map_y_axis_text,
                color_map=color_map
            )
        self.cleared = False
        self.setStartButton()
        self.progressBar.setValue(0)

    def calErrorFunction(self, x, y, z):
        if self.error_map_z_axis_text == cst.OVERLAP:
            return self.calc_error(x, y, z)
        if self.error_map_z_axis_text == cst.POLYNOMIAL_DEGREE:
            return self.calc_error(z, y, x)
        else:
            return self.calc_error(x, z, y)

    def setStartButton(self):
        self.error_map_button.setText("Start")
        self.error_map_button.setStyleSheet("background-color: rgb(0, 54, 125);")

    def setCancelButton(self):
        self.error_map_button.setText("Cancel")
        self.error_map_button.setStyleSheet("background-color: #930000;")

    def toggleStartCancel(self):
        curr_text = self.error_map_button.text()
        if curr_text == "Start":
            self.setCancelButton()
        else:
            self.setStartButton()

    def errorMapHandler(self):
        curr_text = self.error_map_button.text()
        selected_axis = {self.error_map_x_axis_text, self.error_map_y_axis_text}
        if curr_text == "Start":
            if len(selected_axis) == 1:
                qtw.QMessageBox.warning(self, "Invalid Input", "Please choose different axis for x and y")
                return
            z_axis_value = self.z_axis_spinbox.value()
            self.error_map_worker = ErrorMapWorker(
                self.calErrorFunction, self.x_axis_range, self.y_axis_range, z_axis_value
            )
            self.error_map_thread = qtc.QThread()
            self.error_map_worker.currProgress.connect(self._updateProgressbar)
            self.error_map_worker.ready.connect(self.showErrorMap)
            self.error_map_thread.started.connect(self.error_map_worker.run)
            self.error_map_worker.moveToThread(self.error_map_thread)
            self.error_map_thread.start()
            self.setCancelButton()

        if curr_text == "Cancel":
            self.error_map_worker.stop()
            self.setStartButton()
            self.canvas.clear()

    def _updateProgressbar(self, val):
        self.progressBar.setValue(val)

    def _getXAxisText(self):
        return getCheckedRadioButton(self.error_map_x_axis_radio_btns)

    def _getYAxisText(self):
        return getCheckedRadioButton(self.error_map_y_axis_radio_btns)

    def _getZAxisText(self):
        selected_axis = {self.error_map_x_axis_text, self.error_map_y_axis_text}
        if cst.OVERLAP not in selected_axis:
            return cst.OVERLAP
        if cst.POLYNOMIAL_DEGREE not in selected_axis:
            return cst.POLYNOMIAL_DEGREE
        if cst.NUMBER_OF_CHUNKS not in selected_axis:
            return cst.NUMBER_OF_CHUNKS

    def _changeAxis(self):
        self.error_map_x_axis_text = self._getXAxisText()
        self.error_map_y_axis_text = self._getYAxisText()
        self.error_map_z_axis_text = self._getZAxisText()

    def _testErrorMap(self):
        error_map = self.calculateErrorMap(
            randomErrorCalculation, [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        )
        self.plotErrorMap(data=error_map)


class ErrorMapCanvas(FigureCanvas):

    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        divider = make_axes_locatable(self.axes)
        self.cax = divider.append_axes("right", size="5%", pad=0.1)
        self.cax.yaxis.tick_right()
        self.fig.canvas.toolbar_visible = False
        for spine in ['right', 'top', 'left', 'bottom']:
            self.axes.spines[spine].set_color('gray')
            self.cax.spines[spine].set_color('gray')

        self.color_bar = None
        self.progress = 0
        self.canceled = False
        super().__init__(self.fig)

    def _errorMapAxesSetting(self, x_axis_label, y_axis_label, data):
        self.axes.tick_params(
            axis='both',
            which='both',
            bottom=True,
            left=True,
            right=False,
            top=False,
            labelbottom=True
        )

        if (x_axis_label, y_axis_label) in cst.LABEL_PAIRS:
            data = np.transpose(data)
        self.axes.set_title('Error Map')
        self.axes.set_xticks(np.arange(30))
        self.axes.set_xticklabels(cst.TICKS)
        self.axes.set_yticks(np.arange(30))
        self.axes.set_yticklabels(cst.TICKS)
        self.axes.set_xlabel(x_axis_label)
        self.axes.set_ylabel(y_axis_label)
        return data

    def _showColorBar(self, color_map):
        self.color_bar = self.fig.colorbar(
            cm.ScalarMappable(norm=colors.Normalize(), cmap=color_map), ax=self.axes, cax=self.cax
        )

    def plot(self,
             data=np.zeros(shape=(10, 10)),
             color_map="inferno",
             x_axis=cst.NUMBER_OF_CHUNKS,
             y_axis=cst.POLYNOMIAL_DEGREE):
        self.clear()

        data = self._errorMapAxesSetting(x_axis, y_axis, data)
        error_map_plot = self.axes.imshow(data, cmap=color_map, origin='lower')
        self._showColorBar(color_map)

        self.draw()
        return error_map_plot

    def clear(self):
        self.cleared = True
        self.axes.cla()
        self.cax.cla()
        self.cax.yaxis.tick_right()
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.draw()


class ErrorMapWorker(qtc.QObject):
    currProgress = qtc.pyqtSignal(int)
    ready = qtc.pyqtSignal(bool, object)

    def __init__(self, calc_error, x_axis_range, y_axis_range, z_axis_value):
        super().__init__()
        self.canceled = False
        self.progress = 0.0
        self.calErrorFunction = calc_error
        self.x_range, self.y_range = x_axis_range, y_axis_range
        self.z_axis_value = z_axis_value

    def _calculateErrorMap(self):
        self.progress = 0.0
        self.canceled = False
        error_map_data = np.zeros(shape=(len(self.x_range), len(self.y_range)))
        total_num_errors = len(self.x_range) * len(self.y_range)
        progress_step = 100.0 / total_num_errors
        for x_idx, x in enumerate(self.x_range, start=0):
            for y_idx, y in enumerate(self.y_range, start=0):
                if not self.canceled:
                    error = self.calErrorFunction(x, y, self.z_axis_value)
                    error_map_data[y_idx][x_idx] = error
                    self.progress += progress_step
                    self.currProgress.emit(self.progress)
                else:
                    return 0
        return error_map_data

    def setErrorRanges(self, x_range, y_range):
        self.x_range = x_range
        self.y_range = y_range

    @qtc.pyqtSlot()
    def run(self):
        error_map_data = self._calculateErrorMap()
        self.ready.emit(self.canceled, error_map_data)

    def stop(self):
        self.canceled = True

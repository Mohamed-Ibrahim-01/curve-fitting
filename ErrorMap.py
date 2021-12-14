import time
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
from matplotlib.figure import Figure
import PyQt5.QtCore as qtc
plt.style.use('dark_background')


class ErrorMap(FigureCanvas):
    ready = qtc.pyqtSignal()
    progressChanged = qtc.pyqtSignal(int)

    def __init__(self, parent=None, width=4, height=3, dpi=100):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        for spine in ['right', 'top', 'left', 'bottom']:
            self.axes.spines[spine].set_color('gray')
        self.progress = 0
        self.canceled = False
        super().__init__(self.fig)

    def plotErrorMap(self,
                     data=np.zeros(shape=(10,10)),
                     color_map="inferno",
                     figsize=(4,3),
                     x_axis="Number of Chunks",
                     y_axis="Polynomial Degree"):
        self.clear()
        self.axes.set_title('Error Map')
        self.axes.set_xlabel(x_axis)
        self.axes.set_ylabel(y_axis)
        self.axes.set_xticks(np.arange(30))
        self.axes.set_xticklabels(np.arange(1, 31), rotation=90)
        self.axes.set_yticks(np.arange(30))
        self.axes.set_yticklabels(np.arange(1, 31))
        if x_axis == "Polynomial Degree":
            data = np.transpose(data)
        error_map_plot = self.axes.imshow(data, cmap=color_map, origin='lower')
        divider = make_axes_locatable(self.axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.fig.colorbar(
            cm.ScalarMappable(norm=colors.Normalize(), cmap=color_map), ax=self.axes, cax=cax
        )
        self.fig.canvas.toolbar_visible = False
        self.draw()
        self.ready.emit()
        return error_map_plot

    def calculateErrorMap(self, calError, x_range, y_range, z=5):
        self.progress = 0.0
        self.canceled = False
        error_map_data = np.zeros(shape=(len(x_range), len(y_range)))
        total_num_errors = len(x_range)*len(y_range)
        PROGRESS_STEP = 100.0/total_num_errors
        for x_idx, x in enumerate(x_range, start=0):
            for y_idx, y in enumerate(y_range, start=0):
                if not self.canceled:
                    error = calError(x, y, z)
                    error_map_data[x_idx][y_idx] = error
                    self.progress += PROGRESS_STEP
                    self.progressChanged.emit(self.progress)
                else: return 0
        return error_map_data

    def clear(self):
        self.axes.cla()
        self.draw()

    def randomErrorCalculation(self, *args, **kwargs):
        return random.uniform(0, 1)

    def testErrorMap(self):
        error_map = self.calculateErrorMap(self.randomErrorCalculation, [1,2,3,4,5,6], [1,2,3,4,5,6,7,8,9,10])
        self.plotErrorMap(data=error_map)


class ErrorMapWorker(qtc.QObject):
    currProgress = qtc.pyqtSignal(int)
    ready = qtc.pyqtSignal(bool, object)

    def __init__(self, calError, z_axis, z_axis_value):
        super().__init__()
        self.error_map = ErrorMap()
        self.calErrorFunction = calError
        self.x_range, self.y_range = np.arange(30)+1, np.arange(30)+1
        self.z_axis_value = z_axis_value
        self.z_axis = z_axis
        self.error_map.progressChanged.connect(self.updateProgress)


    def updateProgress(self, progress):
        self.currProgress.emit(progress)

    def setErrorRanges(self, x_range, y_range):
        self.x_range = x_range
        self.y_range = y_range

    @qtc.pyqtSlot()
    def run(self):
        error_map_data = self.error_map.calculateErrorMap(
            self.calErrorFunction, self.x_range, self.y_range, self.z_axis_value
        )
        self.ready.emit(self.error_map.canceled, error_map_data)

    def stop(self):
        self.is_running = False
        self.error_map.canceled = True

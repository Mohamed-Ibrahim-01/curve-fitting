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
        self.progress = 0
        super().__init__(self.fig)
        self.fig.tight_layout()

    def plotErrorMap(self, data=np.zeros(shape=(10,10)), color_map="inferno", figsize=(4,3)):
        self.axes.imshow(data,cmap=color_map)
        divider = make_axes_locatable(self.axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(), cmap=color_map), ax=self.axes, cax=cax)
        self.fig.canvas.toolbar_visible = False
        self.draw()
        self.ready.emit()

    def calculateErrorMap(self, calError, x_range, y_range):
        self.progress = 0.0
        error_map_data = np.zeros(shape=(len(x_range), len(y_range)))
        total_num_errors = len(x_range)*len(y_range)
        for x_idx, x in enumerate(x_range, start=0):
            for y_idx, y in enumerate(y_range, start=0):
                error = calError(x, y)
                error_map_data[x_idx][y_idx] = error
                self.progress += (1/total_num_errors)*100.0
                print("**********************")
                print(self.progress)
                self.progressChanged.emit(self.progress)
        return error_map_data

    def randomErrorCalculation(self, x, y):
        return random.uniform(0, 1)

    def testErrorMap(self):
        error_map = self.calculateErrorMap(self.randomErrorCalculation, [1,2,3,4,5,6], [1,2,3,4,5,6,7,8,9,10])
        error_map[1][1] = 0
        self.plotErrorMap(data=error_map)


class ThreadedErrorMap(qtc.QThread):
    currProgress = qtc.pyqtSignal(int)
    ready = qtc.pyqtSignal(object)

    def __init__(self, calError, parent=None ):
        super(ThreadedErrorMap, self).__init__(parent)
        self.error_map = ErrorMap()
        self.calErrorFunction = calError
        self.is_running = True
        self.x_range, self.y_range = np.arange(30)+1, np.arange(30)+1
        self.error_map.progressChanged.connect(self.updateProgress)

    def updateProgress(self, progress):
        if self.is_running:
            self.currProgress.emit(progress)
        else: self.currProgress.emit(0)

    def setErrorRanges(self, x_range, y_range):
        self.x_range = x_range
        self.y_range = y_range

    def run(self):
        if self.is_running:
            error_map_data = self.error_map.calculateErrorMap(
                self.calErrorFunction, self.x_range, self.y_range
            )
            self.ready.emit(error_map_data)

    def stop(self):
        self.is_running = False
        self.quit()

import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
from matplotlib.figure import Figure
plt.style.use('dark_background')


class ErrorMap(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.fig.tight_layout()

    def plotErrorMap(self, data=np.zeros(shape=(10,10)), color_map="inferno", figsize=(10,7)):
        self.axes.imshow(data,cmap=color_map)
        divider = make_axes_locatable(self.axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(), cmap=color_map), ax=self.axes, cax=cax)
        self.fig.canvas.toolbar_visible = False
        self.draw()

    def calculateErrorMap(self, calError, x_range, y_range):
        error_map = np.zeros(shape=(len(x_range), len(y_range)))
        for x_idx, x in enumerate(x_range, start=0):
            for y_idx, y in enumerate(y_range, start=0):
                error_map[x_idx][y_idx] = calError(x, y)
        return error_map

    def randomErrorCalculation(self, x, y):
        return random.uniform(0, 1)

    def testErrorMap(self):
        error_map = self.calculateErrorMap(self.randomErrorCalculation, [1,2,3,4,5,6], [1,2,3,4,5,6,7,8,9,10])
        error_map[1][1] = 0
        self.plotErrorMap(data=error_map)


import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors


def plotErrorMap(data=np.zeros(shape=(10,10)), color_map="inferno", figsize=(10,7)):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.imshow(data,cmap=color_map)
    fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(), cmap=color_map), ax=ax)
    fig.canvas.toolbar_visible = False
    plt.show()


def calculateErrorMap(calError, x_range, y_range):
    error_map = np.zeros(shape=(len(x_range), len(y_range)))
    for x_idx, x in enumerate(x_range, start=0):
        for y_idx, y in enumerate(y_range, start=0):
            error_map[x_idx][y_idx] = calError(x, y)
    return error_map


def randomErrorCalculation(x, y):
    return random.uniform(0, 1)


def testErrorMap():
    error_map = calculateErrorMap(randomErrorCalculation, [1,2,3,4,5,6], [1,2,3,4,5,6,7,8,9,10])
    error_map[1][1] = 0
    plotErrorMap(data=error_map)

testErrorMap()

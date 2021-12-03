import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

data = ()

def plotErrorMap(data=np.zeros(shape=(10,10)), color_map="inferno", figsize=(10,7)):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.imshow(data,cmap=color_map)
    fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(), cmap=color_map), ax=ax)
    fig.canvas.toolbar_visible = False
    plt.show()

plotErrorMap()

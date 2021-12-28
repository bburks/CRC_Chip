import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import numpy as np



def make_bounds(nums):
    bounds = []
    l = len(nums)
    numIt = iter(nums)
    numIt2 = iter(nums)
    next(numIt)

    for i in range(l - 1):
        low = next(numIt2)
        high = next(numIt)
        halfDiff = (high - low) / 2
        if i == 0:
            bounds.append(low - halfDiff)
        bounds.append(low + halfDiff)
        if i == l - 2:
            bounds.append(high + halfDiff)

    return np.array(bounds)

def make_square_plot(xs, ys, xlabel, ylabel, dataList, path):
    yBounds = make_bounds(ys)
    xBounds = make_bounds(xs)
    dataList = np.array(dataList)
    fig, ax = plt.subplots()
    print(dataList)

    plot = ax.pcolormesh(xBounds, yBounds, dataList, cmap='Blues')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.colorbar(plot)
    fig.savefig(path)


if __name__ == "__main__":
    xs = [1, 2]
    ys = [1, 3, 5]
    dataList = [[1, 2], [3, 4], [5, 6]]
    path = 'output_files/tests/figures/1'
    plot(ys, xs, dataList, path)

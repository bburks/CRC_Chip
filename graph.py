import matplotlib.pyplot as plt
import math

def my_log(int, base = 10):
    if int <= 0:
        return -1
    else:
        return math.log(int, base)

def get_next_power_of_two(num):
    nextPowerOfTwo = 2 ** math.ceil(math.log(num, 2))
    return nextPowerOfTwo

class Graph:

    def __init__(self, xData, yDatas, yErrors, labels,  xlabel = '', ylabel = '', name = ''):
        self.xData = xData
        self.yDatas = yDatas
        self.yErrors = yErrors
        self.labels = labels
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.name = name

    # useful for creating the Graph object

    def add_plot(self, yData, yError):
        self.yDatas.append(yData)
        self.yError.append(yError)

    # some helper functions

    def get_max_data(self):
        sup = 0
        for i, data in enumerate(self.yDatas):
            for j, datum in enumerate(data):
                yVal = datum + self.yErrors[i][j]
                sup = max(sup, yVal)
        return sup
    # actually making visual graphs out of the Graph object

    def stealth_graph(self, sizing = 160, ymax = 'default'):
        fig = plt.figure()

        ax = fig.add_subplot(111)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.name)

        if ymax == 'default':
            ymax = get_next_power_of_two(self.get_max_data())
        ax.set_ylim(0, ymax)

        for i, ydata in enumerate(self.yDatas):
            ax.errorbar(self.xData, ydata, yerr = self.yErrors[i], label = self.labels[i], capsize = 5)
        ax.legend()
        return [fig, ax]

    def save_graph(self, path, sizing = 160, ymax = 'default'):
        [fig, _] = self.stealth_graph(sizing = sizing, ymax = ymax)
        fig.savefig(path, transparent=False, dpi=sizing, bbox_inches="tight")
        plt.close()

    def save_no_errors_graph(self, path, sizing = 160):
        fig = plt.figure()

        ax = fig.add_subplot(111)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.name)
        for i, ydata in enumerate(self.yDatas):
            ax.plot(self.xData, ydata, label = self.labels[i])
        ax.legend()
        fig.savefig(path, transparent=False, dpi=sizing, bbox_inches="tight")
        plt.close()

    def save_log_graph(self, path, sizing = 160):
        yDataList = []
        upperErrorsList = []
        lowerErrorsList = []
        for i, yData in enumerate(self.yDatas):
            newYData = []
            upperErrors = []
            lowerErrors = []

            for j, datum in enumerate(yData):
                error = self.yErrors[i][j]
                newDatum = my_log(datum, 2)

                upper = datum + error
                lower = datum - error

                upperError = my_log(upper, 2) - newDatum
                lowerError = newDatum - my_log(lower, 2)

                newYData.append(newDatum)
                upperErrors.append(upperError)
                lowerErrors.append(lowerError)


            yDataList.append(newYData)
            upperErrorsList.append(upperErrors)
            lowerErrorsList.append(lowerErrors)

        fig = plt.figure()

        ax = fig.add_subplot(111)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.name)

        for i, yData in enumerate(yDataList):
            errors = [lowerErrorsList[i], upperErrorsList[i]]
            ax.errorbar(self.xData, yData, yerr = errors, label = self.labels[i], capsize = 5)

        ax.legend()
        fig.savefig(path, transparent=False, dpi=sizing, bbox_inches="tight")
        plt.close()

    # returns a new object containing all the plots (yDatas with yErrors)
    # from Graph objects self and g

    def combine(self, g):
        newXData = self.xData
        newYdatas = self.yDatas + g.yDatas
        newYErrors = self.yErrors + g.yErrors
        newLabels = self.labels + g.labels
        newXLabel = self.xlabel
        newYLabel = self.ylabel
        newName = self.name

        newGraph = Graph(newXData, newYdatas, newYErrors, newLabels, newXLabel, newYLabel, newName)

        return newGraph


# this does not work right now. Can delete if desired. Intended to help make
# comparisons of data (multiple graphs on one image)
class SuperGraph:
    def __init__(self, graphsList):
        self.w = len(graphsList[0])
        self.h = len(graphsList)
        self.graphsList = graphsList



    def save(self, path, sizing = 160):
        fig, axs = plt.subplots(self.h, self.w)

        for h in range(self.h):
            for w in range(self.w):
                g = self.graphsList[h][w]
                ax = axs[h][w]

                ax.set_xlabel(g.xlabel)
                ax.set_ylabel(g.ylabel)
                ax.set_title(g.name)

                ymax = get_next_power_of_two(g.get_max_data())


                for i, ydata in enumerate(g.yDatas):
                    ax.errorbar(g.xData, ydata, yerr = g.yErrors[i], label = g.labels[i], capsize = 5)
                #ax.legend()


        fig.subplots_adjust(hspace = 0.4




        )
        fig.savefig(path, transparent=False, dpi=sizing, bbox_inches="tight")
        plt.close()

    def save_log(self, path, sizing = 160):
        pass

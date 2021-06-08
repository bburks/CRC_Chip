import matplotlib.pyplot as plt
import math

def my_log(int):
    if int < 1:
        return -1
    else:
        return math.log(int)


class Graph:

    def __init__(self, xData, yDatas, yErrors, labels,  xlabel = '', ylabel = '', name = ''):
        self.xData = xData
        self.yDatas = yDatas
        self.yErrors = yErrors
        self.labels = labels
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.name = name



    def add_plot(self, yData, yError):
        self.yDatas.append(yData)
        self.yError.append(yError)

    def save_graph(self, path, sizing = 160):
        fig = plt.figure()

        ax = fig.add_subplot(111)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.name)
        for i, ydata in enumerate(self.yDatas):
            ax.errorbar(self.xData, ydata, yerr = self.yErrors[i], label = self.labels[i], capsize = 5)
        ax.legend()
        fig.savefig(path, transparent=False, dpi=sizing, bbox_inches="tight")
        plt.close()

    def save_log_graph(self, path, sizing = 160):
        newYdatas = []
        newYerrors = []
        for ydata in self.yDatas:
            newYdata = []
            newYerror = []
            for datum in ydata:
                newYdata.append(my_log(datum))
                newYerror.append(0)
            newYdatas.append(newYdata)
            newYerrors.append(newYerror)


        newGraph = Graph(self.xData, newYdatas, newYerrors, self.labels, xlabel = self.xlabel, ylabel = self.ylabel, name = self.name)
        newGraph.save_graph(path, sizing = sizing)

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


def main():

    testGraph = Graph([0, 1, 2, 3], [[0, 0, 0, 0], [1, 2, 4, 3]], ['0', '1'])
    testGraph.save_graph('output_files/test/1.png')

    secondGraph = Graph([0, 1, 2, 3], [[0, 0, 0, 0], [1, 2, 5, 20]], ['0', '1'])
    secondGraph.save_graph('output_files/test/2.png')
if __name__ == "__main__":
    main()

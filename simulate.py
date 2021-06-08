#import matplotlib.pyplot as plt
import numpy as np
import model
import crc_models as cm
import os
import copy
import matplotlib.pyplot as plt
import crc_models
import graph


def divide(list_of_lists, d):
    for list in list_of_lists:
        for i, num in enumerate(list):
            list[i] = num / d
    return list_of_lists

def divide_list(list, d):
    for i, num in enumerate(list):
        list[i] = num / d
    return list


def make_average_graph(model, duration, swaptimes, attemptCount, dataCount = 1000):


    populationCount = len(model.get_populations())
    labels = []
    historySums = []
    historySquareSums = []
    for pop in model.get_populations():
        historySums.append([0] * (dataCount + 1))
        historySquareSums.append([0] * (dataCount + 1))
        labels.append(pop.label)
        #initializes historySums and historySquareSums and creates labels


    for _ in range(attemptCount):


        if _ % 100 == 0:
            print('starting attempt number ' + str(_))

        modelToSim = copy.deepcopy(model)
        modelToSim.run(duration, swaptimes, dataCount)


        for i, pop in enumerate(modelToSim.get_populations()):

            for j in range(dataCount + 1):
                num = pop.get_history()[j]
                historySums[i][j] = historySums[i][j] + num
                historySquareSums[i][j] = historySquareSums[i][j] + (num ** 2)

    timeHistory = modelToSim.get_time_history()

    mean = divide(historySums, attemptCount)
    meanSquare = divide(historySquareSums, attemptCount)



    standardDev = []
    for j in range(populationCount):
        standardDev.append([])
        for i in range(dataCount + 1):

            m1 = mean[j][i]
            m2 = meanSquare[j][i]
            v = m2 - (m1 ** 2)
            std = v ** 0.5
            standardDev[j].append(std)





    res = graph.Graph(timeHistory, mean, standardDev, labels)

    return res

def make_averages(model, duration, swaptimes, attemptCount, dataCount = 1000, pathStart = 'output_files/'):

    res = make_average_graph(model, duration, swaptimes, attemptCount, dataCount)
    res.save_graph(pathStart + 'average_with_error')

def make_IR_graph(model, duration, swaptimes, attemptCount, dataCount = 1000, label = ''):

    populationCount = len(model.get_populations())
    labels = [label]
    IRSums = [0] * (dataCount + 1)
    IRSquareSums = [0] * (dataCount + 1)


    for _ in range(attemptCount):
        modelToSim = copy.deepcopy(model)
        modelToSim.run(duration, swaptimes, dataCount)

        pops = modelToSim.get_populations()
        epithelialStart = pops[0].get_history()[0] + pops[1].get_history()[0]
        endothelialStart = pops[2].get_history()[0]
        if endothelialStart == 0:
            endothelialStart = 1
        invasionRatioInitial = endothelialStart / epithelialStart

        for i in range(dataCount + 1):
            pops = modelToSim.get_populations()
            epithelialCount = pops[0].get_history()[i] + pops[1].get_history()[i]
            endothelialCount = pops[2].get_history()[i]

            if endothelialCount == 0:
                endothelialCount = 1


            invasionRatio = endothelialCount / (epithelialCount * invasionRatioInitial)

            IRSums[i] = IRSums[i] + invasionRatio
            IRSquareSums[i] = IRSquareSums[i] + (invasionRatio ** 2)


    timeHistory = modelToSim.get_time_history()
    means = divide_list(IRSums, attemptCount)
    meanSquares = divide_list(IRSquareSums, attemptCount)
    IRStdDvs = []
    for j in range(dataCount + 1):
        IRVariance = meanSquares[j] - (means[j] ** 2)

        IRStdDv = IRVariance ** 0.5
        IRStdDvs.append(IRStdDv)


    res = graph.Graph(timeHistory, [means], [IRStdDvs], labels)
    return res

def make_IR(model, duration, swaptimes, attemptCount, dataCount = 1000, label = '', pathStart = 'output_files/'):
    res = make_IR_graph(model, duration, swaptimes, attemptCount, dataCount, label)
    res.save_graph(pathStart + 'inavsion_ratio')

def make_IRs_from_paper(model, attemptCount, pathStart = 'output_files/'):
    duration = 6
    dataCount = 3
    swapTimesList = [[0], [], [0, 2], [2], [0, 4]]
    labels = ['D0-D6 Stretch', 'D0-D6 No Stretch', 'D0-D2 Stretch', 'D2-D6 Stretch', 'D0-D4 Stetch']

    for i, swapTimes in enumerate(swapTimesList):

        next = make_IR_graph(model, duration, swapTimes, attemptCount, dataCount, labels[i])
        if i == 0:
            res = next
        else:
            res = res.combine(next)


    res.xlabel = 'Days'
    res.ylabel = 'Log Invasion Ratio'
    res.save_log_graph(pathStart + 'inavsion_ratios')

    pass



def simulate(model, duration):

    detailedCount = 10
    totalSimulations = 100
    dataPoints = 1000




    try:
        os.mkdir('output_files')
    except:
        print("the directory already exists")


    #crc.run(duration)
    #crc.show_history()

    #part 1 - make detailed graphs

    for i in range(detailedCount):

        modelToSim = copy.deepcopy(model)

        modelToSim.run(duration, dataCount = dataPoints - 1)
        #modelToSim.make_history_graph()
        modelToSim.save_history_graph('output_files/sim' + str(i + 1), graphName = 'simulation ' + str(i + 1))
        #modelToSim.show_history_graph()
        plt.close()

    """

    #part 2 - run a lot of simulations and make mean, meansquare data



    sumTotal = []
    sumSquareTotal = []
    standardDev = []
    upperBounds = []
    lowerBounds = []
    for pop in modelToSim.get_populations():
        sumTotal.append([0] * dataPoints)
        sumSquareTotal.append([0] * dataPoints)
        standardDev.append([0] * dataPoints)
        upperBounds.append([0] * dataPoints)
        lowerBounds.append([0]*dataPoints)



    for _ in range(totalSimulations):


        modelToSim = copy.deepcopy(model)

        modelToSim.run(duration, dataCount = dataPoints - 1)

        for i, pop in enumerate(modelToSim.get_populations()):
            for j, popCount in enumerate(pop.get_history()):
                sumTotal[i][j] += popCount
                sumSquareTotal[i][j] += (popCount ** 2)

    timeHistory = modelToSim.get_time_history()
    meanHistory = divide(sumTotal, totalSimulations)
    meanSquaredHistory = divide(sumSquareTotal, totalSimulations)




    for i in range(len(standardDev)):
        for j in range(len(standardDev[i])):
            temp = meanSquaredHistory[i][j] \
                - meanHistory[i][j] ** 2
            standardDev[i][j] = temp ** 0.5
            upperBounds[i][j] = meanHistory[i][j] + standardDev[i][j]
            lowerBounds[i][j] = meanHistory[i][j] - standardDev[i][j]


    #part 3 - make an averages plot

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title("average population growth over time")
    ax.set_xlabel("time")
    ax.set_ylabel("population count")

    for i, pop in enumerate(model.get_populations()):
        ax.plot(timeHistory, meanHistory[i], label = pop.label)

    ax.legend()
    fig.savefig("output_files/simMean", transparent=False, dpi=160, bbox_inches="tight")
    plt.close()

    #part 4 - make a expectation range plot

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title("average population growth over time +- standard deviation")
    ax.set_xlabel("time")
    ax.set_ylabel("population count")
    colors = ['blue', 'orange', 'green']
    for i, pop in enumerate(model.get_populations()):
        ax.plot(timeHistory, upperBounds[i], label = pop.label + " upper bound", color = colors[i])
        ax.plot(timeHistory, lowerBounds[i], label = pop.label + " lower bound", color = colors[i])

    ax.legend()
    fig.savefig("output_files/simBounds", transparent=False, dpi=160, bbox_inches="tight")
    plt.close()

    """
    #print(meanHistory)
    #print(meanSquaredHistory)
    #print(standardDev)


    print('done')

def do_a_numbers_simulation():
    birthRate = 1.3
    deathRate = 1
    growToGoRate = 0.1
    goToGoneRate = 0.1
    peristalsisModifier = 0
    startingGrow = 100
    startingGo = 0
    startingGone = 0
    duration = 8
    swaptimes = [2, 4, 6]
    attemptCount = 100
    dataCount = 4


    crc = cm.InheritablePeristalsis(birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone)

    make_averages(crc, duration, swaptimes, attemptCount, dataCount)


def main():

    birthRate = 1.01
    deathRate = 1
    growToGoRate = 0.1
    goToGoneRate = 0.01
    peristalsisModifier = 0.03
    startingGrow = 1000
    startingGo = 0
    startingGone = 0
    duration = 6
    swaptimes = [0, 2, 4]
    attemptCount = 100
    dataCount = 3


    crc = cm.InheritablePeristalsis(birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone)

    make_IRs_from_paper(crc, attemptCount)

if __name__ == "__main__":
    main()

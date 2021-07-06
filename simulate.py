import numpy as np
import model
import crc_models as cm
import os
import copy
import matplotlib.pyplot as plt
import crc_models
import graph
import csv
import math







#make a decent model

def make_a_two_pop_log():

    params = {
    'higher birthrate' : 1,
    'lower birthrate' : 0.75,
    'birthrate swaps at' : 25000,
    'deathrate' : 0.5,
    'go to gone' : 0,
    'go to gone peristalsis' : 0.002,
    'starting go' : 8500,
    'starting gone' : 15,
    }


    twoPopLog = crc_models.TwoPopLogistic(params)
    return twoPopLog

def make_a_three_pop_noninheritable_log():
    params = {
    'higher birthrate' : 1,
    'lower birthrate' : 0.75,
    'birthrate swaps at' : 25000,
    'deathrate' : 0.5,
    'grow to go' : 0.001,
    'grow to go peristalsis' : 0.004,
    'go to gone' : 1,
    'starting grow' : 8500,
    'starting go' : 0,
    'starting gone' : 15,
    }

    threePopLog = crc_models.ThreePopLogisticNonInheritable(params)
    return threePopLog

def make_a_three_pop_inheritable_log():
    params = {
    'higher birthrate' : 1,
    'lower birthrate' : 0.75,
    'birthrate swaps at' : 25000,
    'deathrate' : 0.5,
    'grow to go' : 0.001,
    'grow to go peristalsis' : 0.004,
    'go to gone' : 1,
    'starting grow' : 8500,
    'starting go' : 0,
    'starting gone' : 15,
    }

    threePopLog = crc_models.ThreePopLogisticInheritable(params)
    return threePopLog

#helper functions

def divide(list_of_lists, d):
    for list in list_of_lists:
        for i, num in enumerate(list):
            list[i] = num / d
    return list_of_lists

def divide_list(list, d):
    for i, num in enumerate(list):
        list[i] = num / d
    return list

#run simulations

def make_average_graph(model, duration, swaptimes, attemptCount, dataCount = 1000, dataPath = 'internal_files/graphData'):


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



        print('starting attempt number ' + str(_))

        modelToSim = copy.deepcopy(model)
        modelToSim.run(duration, dataCount, swaptimes)


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




    with open(dataPath + '.csv', 'w', newline='') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow(['time'] + timeHistory)
        for i, pop in enumerate(model.get_populations()):
            csvWriter.writerow([pop.label] + mean[i])
    with open(dataPath + 'Error.csv', 'w', newline='') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow(['time'] + timeHistory)
        for i, pop in enumerate(model.get_populations()):
            csvWriter.writerow([pop.label] + standardDev[i])


    res = graph.Graph(timeHistory, mean, standardDev, labels)

    return res

def make_averages(model, duration, swaptimes, attemptCount, dataCount = 1000, path = 'output_files/average'):

    res = make_average_graph(model, duration, swaptimes, attemptCount, dataCount)
    res.save_graph(path)

def make_IR_graph(model, duration, swaptimes, attemptCount, dataCount = 1000, label = '', path = 'output_files/average'):

    populationCount = len(model.get_populations())
    labels = [label]
    IRSums = [0] * (dataCount + 1)
    IRSquareSums = [0] * (dataCount + 1)


    for _ in range(attemptCount):
        modelToSim = copy.deepcopy(model)
        modelToSim.run(duration, dataCount, swaptimes)

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

def make_IR(model, duration, swaptimes, attemptCount, dataCount = 1000, label = '', path = 'output_files/invasion_ratio'):
    res = make_IR_graph(model, duration, swaptimes, attemptCount, dataCount, label)
    res.save_graph(path)
    res.save_log_graph(path + '_log')

def make_IRs_from_paper(model, attemptCount, path = 'output_files/invasion_ratios'):
    duration = 6
    dataCount = 3
    swapTimesList = [[0], [], [0, 2], [2], [0, 4]]
    labels = ['D0-D6-Stretch', 'D0-D6-No-Stretch', 'D0-D2-Stretch', 'D2-D6-Stretch', 'D0-D4-Stetch']

    for i, swapTimes in enumerate(swapTimesList):
        print('currently working on ' + labels[i])
        next = make_IR_graph(model, duration, swapTimes, attemptCount, dataCount, labels[i])
        if i == 0:
            res = next
        else:
            res = res.combine(next)


    res.xlabel = 'Days'
    res.ylabel = 'Invasion Ratio'
    res.save_graph(path)
    res.save_log_graph(path + '_logVersion')
    pass

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

def simulate_to_csv(model, duration, swapTimesList, attemptCount, dataCount, csvWriter, title):

    for j, swapTimes in enumerate(swapTimesList):

        for i in range(attemptCount):
            modelCopy = copy.deepcopy(model)
            modelCopy.run(duration, dataCount, swapTimes)

            if i == 0 and j == 0:

                titleRow = ['condition', 'experiment']
                for pop in modelCopy.get_populations():
                    for time in modelCopy.get_time_history():
                        titleRow.append('t=' + str(time) + ' ' + pop.label)
                csvWriter.writerow(titleRow)

            nextRow = [j + 1, i + 1]
            for pop in modelCopy.get_populations():
                nextRow.extend(pop.get_history())
            csvWriter.writerow(nextRow)

def make_one_csv(model, duration, swapTimes, dataCount, path):
    modelToSim = copy.deepcopy(model)
    modelToSim.run(duration, dataCount, swapTimes)

    with open(path + '.csv', 'w', newline = '') as data:
        dataWriter = csv.writer(data)

        firstLine = ['time'] + modelToSim.get_time_history()
        dataWriter.writerow(firstLine)

        for pop in modelToSim.get_populations():
            nextLine = [pop.label] + pop.get_history()
            dataWriter.writerow(nextLine)

def make_many_csvs(model, duration, swapTimes, dataCount, attemptCount, path):
    for i in range(attemptCount):
        make_one_csv(model, duration, swapTimes, dataCount, path + str(i + 1))

def make_averages_of_csvs(attemptCount, path):


    sumsList = []
    squaresumsList = []
    times = []
    labels = []
    errors = []
    averages = []

    with open(path + '1.csv', newline = '') as firstData:
        reader = csv.reader(firstData)
        firstRow = next(reader)
        times = []

        for time in firstRow[1:]:
            times.append(float(time))

        labels.append(firstRow[0])





        for nextRow in reader:
            labels.append(nextRow[0])

            sums = []
            squareSums = []
            for datum in nextRow[1:]:
                sums.append(float(datum))
                squareSums.append(float(datum) ** 2)
            sumsList.append(sums)
            squaresumsList.append(squareSums)

    for i in range(2, attemptCount + 1):

        with open(path + str(i) + '.csv') as nextData:
            reader = csv.reader(nextData)
            next(reader)

            for j, row in enumerate(reader):
                for k, datum in enumerate(row[1:]):

                    sumsList[j][k] = sumsList[j][k] + float(datum)
                    squaresumsList[j][k] = squaresumsList[j][k] + float(datum) ** 2

    for i, row in enumerate(sumsList):
        errors.append([])
        averages.append([])
        for j, datum in enumerate(row):
            average = datum / attemptCount
            error = ((squaresumsList[i][j] / attemptCount) - (average ** 2)) ** 0.5
            errors[i].append(error)
            averages[i].append(average)



    with open(path + 'average' + '.csv', 'w', newline = '') as ave:

        aveWriter = csv.writer(ave)

        aveWriter.writerow([labels[0]] + times)

        for i, row in enumerate(averages):
            aveWriter.writerow([labels[i + 1]] + row)

    with open(path + 'error' + '.csv', 'w', newline = '') as error:

        errorWriter = csv.writer(error)

        errorWriter.writerow([labels[0]] + times)

        for i, row in enumerate(errors):
            errorWriter.writerow([labels[i + 1]] + row)

def extract_data_from_csv(path):
    dataList = []
    labels = []
    times = []


    with open(path +'.csv', newline = '') as file:
        reader = csv.reader(file)

        firstRow = next(reader)

        for i, data in enumerate(firstRow):
            if i == 0:
                labels.append(data)
            else:
                times.append(float(data))

        for i, nextRow in enumerate(reader):
            dataList.append([])
            for j, data in enumerate(nextRow):
                if j == 0:
                    labels.append(data)
                else:
                    dataList[i].append(float(data))


        return [times, labels, dataList]

def make_graph_of_csvs(path):

    [times, labels, averagesList] = extract_data_from_csv(path + 'average')
    [timesDupe, labelsDupe, errorsList] = extract_data_from_csv(path + 'error')

    ymax = 0
    for i, row in enumerate(averagesList):
        for j, ave in enumerate(row):
            data = ave + errorsList[i][j]
            if data > ymax:
                ymax = data
    ymax = 2 ** (math.floor(math.log(ymax, 2)) + 1)
    g = graph.Graph(times, averagesList, errorsList, labels[1:])
    g.save_graph(path = path + 'graph', ymax = ymax)
    g.save_log_graph(path = path + 'graph_log')


def analyze_model():
    pass

#actually call the file from the command line

def main1():

    birthRate = 1.3
    deathRate = 1
    growToGoRate = 0.1
    goToGoneRate = 0.1
    peristalsisModifier = 0.1
    startingGrow = 7000
    startingGo = 0
    startingGone = 20
    duration = 6
    swaptimes = [0, 2, 4]
    attemptCount = 10
    dataCount = 3

    crcI = cm.InheritablePeristalsis(birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone)
    crcNI = cm.NonInheritablePeristalsis(birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone)

    make_IRs_from_paper(crcNI, attemptCount, path = 'output_files/invasion_ratios_NI')
    make_IRs_from_paper(crcI, attemptCount, path = 'output_files/invasion_ratios_I')





def main2():
    birthRate = 1.3
    deathRate = 1
    growToGoRate = 0.1
    goToGoneRate = 0.1
    peristalsisModifier = 0.1
    startingGrow = 7000
    startingGo = 0
    startingGone = 10
    duration = 20
    swapTimes = [5, 10, 15]
    attemptCount = 1
    dataCount = 10

    crcI = cm.InheritablePeristalsis(birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone)
    crcNI = cm.NonInheritablePeristalsis(birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone)


    make_IR(crcNI, duration, swapTimes, attemptCount, dataCount = dataCount, path = 'output_files/invasion_ratio_NI')
    make_IR(crcI, duration, swapTimes, attemptCount, dataCount = dataCount, path = 'output_files/invasion_ratio_I')

def main3():

    path = 'output_files/csvs/simulate_to_csv'
    title = '10 simulations with no stretching'
    duration = 6
    swapTimesList = [[0], [2], [0, 2], [0, 4]]
    attemptCount = 10
    dataCount = 3

    #model = make_a_three_pop_noninheritable_log()
    model = make_a_two_pop_log()

    with open(path + '.csv', 'w', newline = '') as f:
        csvWriter = csv.writer(f)




        simulate_to_csv(model, duration, swapTimesList, attemptCount, dataCount, csvWriter, title)

def main4():
    path = 'output_files/graphs/simulate_to_graph_'
    title = '10 simulations with no stretching'
    duration = 6
    swapTimesList = [[0], [2], [0, 2], [0, 4]]
    attemptCount = 10
    dataCount = 3


    model = make_a_three_pop_inheritable_log()
    #model = make_a_three_pop_noninheritable_log()
    #model = make_a_two_pop_log()



    paths = []
    for i in range(len(swapTimesList)):
        paths.append(path + str(i + 1))
    os.mkdir('output_files/graphs/rename_me')
    make_IRs_from_paper(model, attemptCount, 'output_files/graphs/rename_me/invasion_ratios')

def main5():

    path = 'output_files/sims/'
    modelLabel = 'TwoPopLog'
    condition = 'no_stretching'
    duration = 6
    swapTimesList = [[0], [2], [0, 2], [0, 4]]
    attemptCount = 10
    dataCount = 3


    model = make_a_three_pop_inheritable_log()
    #model = make_a_three_pop_noninheritable_log()
    #model = make_a_two_pop_log()



    #make_many_csvs(model, duration, swapTimesList[0], dataCount, attemptCount, path)
    #make_averages_of_csvs(attemptCount, path)
    make_graph_of_csvs(path + modelLabel + '/')
if __name__ == "__main__":
    main5()

import model
import crc_models
import csv_handler
import os
import copy
import graph
import csv
import math
import statistics

#make a decent (eyeball) model

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

def make_a_reversible_inheritable():
    params = {
    'higher birthrate' : 1,
    'lower birthrate' : 0.75,
    'birthrate swaps at' : 25000,
    'deathrate' : 0.5,
    'grow to go' : 0.001,
    'grow to go peristalsis' : 0.004,
    'go to grow' : 0.012,
    'go to gone' : 1,
    'starting grow' : 8500,
    'starting go' : 0,
    'starting gone' : 15,
    }

    reversibleInheritable = crc_models.ReversibleInheritable(params)
    return reversibleInheritable

def make_a_reversible_half_inheritable():
    params = {
    'higher birthrate' : 1,
    'lower birthrate' : 0.75,
    'birthrate swaps at' : 25000,
    'deathrate' : 0.5,
    'grow to go' : 0.001,
    'grow to go peristalsis' : 0.004,
    'go to grow' : 0.012,
    'go to gone' : 1,
    'starting grow' : 8500,
    'starting go' : 0,
    'starting gone' : 15,
    }

    reversibleHalf = crc_models.ReversibleHalfInheritable(params)
    return reversibleHalf

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

# run simulations and write them to CSVs

def make_one_csv(model, duration, swapTimes, dataCount, path):
    modelToSim = copy.deepcopy(model)
    modelToSim.run(duration, dataCount, swapTimes)


    times = modelToSim.get_time_history()
    labels = ['time']
    dataList = []

    for pop in modelToSim.get_populations():
        labels.append(pop.get_label())
        dataList.append(pop.get_history())

    csv_handler.export(times, labels, dataList, path)

def make_many_csvs(model, duration, swapTimes, dataCount, attemptCount, path):
    for i in range(attemptCount):
        make_one_csv(model, duration, swapTimes, dataCount, path + str(i + 1))

def make_many_conditions_csvs(model, duration, swapTimesList, conditionLabels, dataCount, attemptCount, path):

    csv_handler.export(conditionLabels, path + 'condition names')

    for i, swapTimes in enumerate(swapTimesList):

        conditionPath = path + conditionLabels[i] + '/'
        try:
            os.mkdir(conditionPath)
        except:
            pass

        make_many_csvs(model, duration, swapTimes, dataCount, attemptCount, conditionPath)

# analyse simulations

def make_averages_of_csvs(attemptCount, path):


    sumsList = []
    squareSumsList = []
    times = []
    labels = []
    errors = []
    averages = []

    firstPath = path + '1'
    [times, labels, firstDataList] = csv_handler.extract_from_csv(firstPath)

    for row in firstDataList:
        newSumRow = []
        newSquareSumRow = []
        sumsList.append(newSumRow)
        squareSumsList.append(newSquareSumRow)
        for datum in row:
            newSumRow.append(datum)
            newSquareSumRow.append(datum ** 2)

    for i in range(2, attemptCount + 1):
        nextPath = path + str(i)
        [_, __, nextDataList] = csv_handler.extract_from_csv(nextPath)

        for j, row in enumerate(nextDataList):
            for k, datum in enumerate(row):
                sumsList[j][k] = sumsList[j][k] + datum
                squareSumsList[j][k] = squareSumsList[j][k] + (datum ** 2)


    for i, row in enumerate(sumsList):
        errors.append([])
        averages.append([])
        for j, datum in enumerate(row):
            average = datum / attemptCount
            error = ((squareSumsList[i][j] / attemptCount) - (average ** 2)) ** 0.5
            errors[i].append(error)
            averages[i].append(average)

    avePath = path + 'average'
    errorPath = path + 'error'

    csv_handler.export(times, labels, averages, avePath)
    csv_handler.export(times, labels, errors, errorPath)

def make_invasion_ratios(epithelialPopCount, attemptCount, path):

    invasionRatiosComplete = []

    for i in range(1, attemptCount + 1):
        realPath = path + str(i)
        [times, labels, dataList] = csv_handler.extract_from_csv(realPath)
        timeCount = len(times)
        popCount = len(dataList)

        if i == 1:
            for _ in range(timeCount):
                invasionRatiosComplete.append([])

        for j in range(timeCount):
            epithelialCount = 0
            endothelialCount = 0

            for k in range(popCount):
                if k < epithelialPopCount:
                    epithelialCount += dataList[k][j]
                else:
                    endothelialCount += dataList[k][j]

            ratio = endothelialCount / epithelialCount
            if j == 0:
                initialRatio = ratio


            scaledRatio = ratio / initialRatio

            invasionRatiosComplete[j].append(scaledRatio)

    IRAverages = []
    IRErrors = []
    for row in invasionRatiosComplete:
        IRAverages.append(statistics.mean(row))
        IRErrors.append(statistics.stdev(row))

    csv_handler.export(times, ['time', 'ave', 'stdev'], [IRAverages, IRErrors], path + 'invasion_ratios')

def stealth_IR_graph(conditionLabels, path, name = ''):

    averagesList = []
    errorsList = []
    labels = conditionLabels


    for conditionLabel in conditionLabels:
        conditionPath = path + conditionLabel + '/'



        [times, _, dataList] = csv_handler.extract_from_csv(conditionPath + 'invasion_ratios')
        averagesList.append(dataList[0])
        errorsList.append(dataList[1])


    g = graph.Graph(times, averagesList, errorsList, labels, name = name)
    return g

def make_IR_graph(conditionLabels, path, name = ''):

    g = stealth_IR_graph(conditionLabels, path, name = name)
    g.save_graph(path + 'invasion_ratios_graph')
    g.save_log_graph(path + 'invasion_ratios_graph_log')

def make_bad_IR_graph(epithelialPopCount, conditionLabels, path):
    invasionRatiosList = []
    logIRsList = []
    errorsList = []
    for conditionLabel in conditionLabels:
        conditionPath = path + conditionLabel + '/'
        [times, _, dataList] = csv_handler.extract_from_csv(conditionPath + 'average')
        invasionRatios = []
        logIRs = []
        errors = []
        epithelialCounts = []
        endothelialCounts = []
        for i, data in enumerate(dataList):

            for j, datum in enumerate(data):
                if i == 0:
                    epithelialCounts.append(0)
                    endothelialCounts.append(0)

                if i < epithelialPopCount:
                    epithelialCounts[j] = epithelialCounts[j] + datum
                else:
                    endothelialCounts[j] = endothelialCounts[j] + datum

        for i in range(len(dataList[0])):
            unscaledIR = endothelialCounts[i] / epithelialCounts[i]
            if i == 0:
                scale = 1 / unscaledIR
            IR = unscaledIR * scale
            invasionRatios.append(IR)
            logIRs.append(math.log(IR, 2))
            errors.append(0)
        invasionRatiosList.append(invasionRatios)
        logIRsList.append(logIRs)
        errorsList.append(errors)

    g = graph.Graph(times, invasionRatiosList, errorsList, conditionLabels)
    g.save_no_errors_graph(path + 'bad_invasion_ratios_graph')
    g2 = graph.Graph(times, logIRsList, errorsList, conditionLabels)
    g2.save_no_errors_graph(path + 'bad_invasion_ratios_graph_log')


def make_average_graphs(path):

    [times, labels, averagesList] = csv_handler.extract_from_csv(path + 'average')
    [timesDupe, labelsDupe, errorsList] = csv_handler.extract_from_csv(path + 'error')

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

#

def analyse_bio_data(path):
    conditionLabels = csv_handler.extract_line_from_csv(path + 'condition names')

    for conditionLabel in conditionLabels:
        conditionPath = path + conditionLabel + '/'


        attemptCount = 0
        while True:
            try:
                csv_handler.extract_from_csv(conditionPath + str(attemptCount + 1))
            except:
                break

            attemptCount += 1

        make_averages_of_csvs(attemptCount, conditionPath)
        make_invasion_ratios(1, attemptCount, conditionPath)

    make_IR_graph(conditionLabels, path)
    make_bad_IR_graph(1, conditionLabels, path)

def make_comparison_graph(modelMatrix, pathMatrix, conditionLabels, shortNames, path):
    h = len(pathMatrix)
    w = len(pathMatrix[0])
    graphsList = []
    for i in range(h):
        graphsList.append([])
        for j in range(w):
            tempPath = pathMatrix[i][j]
            name = shortNames[i][j]
            g = stealth_IR_graph(conditionLabels, tempPath, name = name)
            graphsList[i].append(g)

    sg = graph.SuperGraph(graphsList)
    sg.save(path)
    print(path)
#actually call the file from the command line

def main():
    path = 'output_files/sims/'
    duration = 6
    swapTimesList = [[0], [], [0, 2], [2], [0, 4]]
    conditionLabels = ['D0-D6 Stretched',
    'D0-D6 Not Stretched',
    'D0-D2 Stretched, D2-D6 Not Stretched',
    'D0-D2 Not Stretched, D2-D6 Stretched',
    'D0-D4 Stretched, D4-D6 Not Stretched']

    attemptCount = 100
    dataCount = 3

    model1 = make_a_three_pop_inheritable_log()
    model2 = make_a_three_pop_noninheritable_log()
    model3 = make_a_two_pop_log()
    model4 = make_a_reversible_inheritable()
    model5 = make_a_reversible_half_inheritable()

    models = [model1, model2, model3]
    epithelialPopCounts = [2, 2, 1]

    conditionCount = len(swapTimesList)


    for i, model in enumerate(models):
        modelPath = path + model.name + '/'
        print(model.name)
        try:
            os.mkdir(modelPath)
        except:
            print(modelPath + ' failed to make')
            pass
        csv_handler.export_line(conditionLabels, modelPath + 'condition names')
        #make_many_conditions_csvs(model, duration, swapTimesList, conditionLabels, dataCount, attemptCount, modelPath)


    for i, model in enumerate(models):
        modelPath = path + model.name + '/'
        for j in range(conditionCount):
            conditionPath = modelPath + conditionLabels[j] + '/'
            make_averages_of_csvs(attemptCount, conditionPath)
            make_invasion_ratios(epithelialPopCounts[i], attemptCount, conditionPath)
            make_average_graphs(conditionPath)

        make_IR_graph(conditionLabels, modelPath, name = model.name)
        make_bad_IR_graph(epithelialPopCounts[i], conditionLabels, modelPath)

def main2():
    path = 'output_files/bio_data/'
    analyse_bio_data(path)

def main3():

    conditionLabels = conditionLabels = ['D0-D6 Stretched',
    'D0-D6 Not Stretched',
    'D0-D2 Stretched, D2-D6 Not Stretched',
    'D0-D2 Not Stretched, D2-D6 Stretched',
    'D0-D4 Stretched, D4-D6 Not Stretched']

    modelMatrix = [['bio', 'ThreePopLogisticInheritable', 'Reversible Inheritable'],
    ['TwoPopLogistic', 'ThreePopLogisticNonInheritable', 'Reversible Half-inheritable']]
    shortNames = [['bio', 'I', 'R'], ['2', 'HI', 'RHI']]

    path = 'output_files/'
    pathMatrix = []
    for i in range(2):
        pathMatrix.append([])
        for j in range(3):
            if i == 0 and j == 0:
                pathMatrix[i].append(path + 'bio_data/')
            else:
                pathMatrix[i].append(path + 'sims/' + modelMatrix[i][j] + '/')
    path = path + 'sims/comparison'
    make_comparison_graph(modelMatrix, pathMatrix, conditionLabels, shortNames, path)


if __name__ == "__main__":
    main()

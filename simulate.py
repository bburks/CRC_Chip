import model
import crc_models
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

# inputs a CSV and outputs [times, labels, dataList]
# dataList is a list of lists.

def extract_from_csv(path):
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

# writes a csv containing times, labels, dataList at the given path

def export_to_csv(times, labels, dataList, path):
    with open(path + '.csv', 'w', newline = '') as file:
        writer = csv.writer(file)

        writer.writerow([labels[0]] + times)

        for i, row in enumerate(dataList):
            writer.writerow([labels[i + 1]] + row)




# run simulations and write them to CSVs

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

def make_many_conditions_csvs(model, duration, swapTimesList, conditionLabels, dataCount, attemptCount, path):

    for i, swapTimes in enumerate(swapTimesList):
        try:
            os.mkdir(path + 'condition_' + str(i + 1) + '/')
        except:
            pass
        label = open(path + 'condition_' + str(i + 1) + '/condition.txt', 'w')
        label.write(conditionLabels[i])
        label.close()
        make_many_csvs(model, duration, swapTimes, dataCount, attemptCount, path + 'condition_' + str(i + 1) + '/')

# analyse simulations

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

def make_invasion_ratios(epithelialPopCount, attemptCount, path):

    invasionRatiosComplete = []

    for i in range(1, attemptCount + 1):
        realPath = path + str(i)
        [times, labels, dataList] = extract_from_csv(realPath)
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

    export_to_csv(times, ['time', 'ave', 'stdev'], [IRAverages, IRErrors], path + 'invasion_ratios')

def make_IR_graph(conditionCount, path):

    averagesList = []
    errorsList = []
    labels = []


    for i in range(1, conditionCount + 1):
        conditionPath = path + 'condition_' + str(i) + '/'
        f = open(conditionPath + 'condition.txt')
        labels.append(f.read())
        f.close()

        [times, _, dataList] = extract_from_csv(conditionPath + 'invasion_ratios')
        averagesList.append(dataList[0])
        errorsList.append(dataList[1])


    g = graph.Graph(times, averagesList, errorsList, labels)
    g.save_graph(path + 'invasion_ratios_graph')
    g.save_log_graph(path + 'invasion_ratios_graph_log')

def make_average_graphs(path):

    [times, labels, averagesList] = extract_from_csv(path + 'average')
    [timesDupe, labelsDupe, errorsList] = extract_from_csv(path + 'error')

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


#actually call the file from the command line

def main():
    path = 'output_files/test/'
    duration = 6
    swapTimesList = [[0], [2], [0, 2], [0, 4], []]
    conditionLabels = ['All stretch', 'D2-D6 stretch', 'D0-D2 stretch', 'D0-D4 stretch', 'No stretch']
    attemptCount = 2
    dataCount = 3


    model1 = make_a_three_pop_inheritable_log()
    model2 = make_a_three_pop_noninheritable_log()
    model3 = make_a_two_pop_log()

    models = [model1, model2, model3]
    epithelialPopCounts = [2, 2, 1]

    conditionCount = len(swapTimesList)


    for i, model in enumerate(models):
        modelPath = path + model.name + '/'
        print(model.name)
        try:
            os.mkdir(path + model.name + '/')
        except:
            pass

        make_many_conditions_csvs(model, duration, swapTimesList, conditionLabels, dataCount, attemptCount, modelPath)


    for i, model in enumerate(models):
        modelPath = path + model.name + '/'
        for j in range(1, conditionCount + 1):
            conditionPath = modelPath + 'condition_' + str(j) + '/'
            make_averages_of_csvs(attemptCount, conditionPath)
            make_invasion_ratios(epithelialPopCounts[i], attemptCount, conditionPath)
            make_average_graphs(conditionPath)
        make_IR_graph(conditionCount, modelPath)

if __name__ == "__main__":
    main()

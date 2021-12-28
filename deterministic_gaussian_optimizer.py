"""This file is to find the optimal parameters if we are trying to minimize
the L2 norm of the vector with entries
(observed data / expected average data)  - 1.
Left in because some of the code might someday be useful, but needs to be
cleaned up and/or implemented properly to use (algorithms similar but
not same as those in referenced TRANSCOMPP/cellTrans papers)
"""




import numpy as np
import math
from scipy.linalg import expm, inv, logm
#from scipy.linalg import inv
import csv_handler as csv
import visual_handler
import scipy.optimize as opt
import copy
from scipy.optimize import minimize

class Parameter:

    def __init__(self, actual, lower, upper, label):
        self.actual = actual
        self.lower = lower
        self.upper = upper
        self.label = label
        self.isStochastic = (lower != upper)
    def get_value(self):
        return self.actual

    def get_bounds(self):
        return (self.lower, self.upper)

    def get_label(self):
        return self.label

    def is_stochastic(self):
        return  self.isStochastic

    def resample(self):
        r = np.random.random()
        self.actual = r * (self.upper - self.lower) + self.lower

    def make_copy(self):
        param = copy.deepcopy(self)
        return param

    def make_resampled_copy(self):
        param = copy.deepcopy(self)
        param.resample()
        return param

    def make_value_copy(self, value):
        param = copy.deepcopy(self)
        param.actual = value
        return param

class Parameters:

    def __init__(self, params):
        self.params = params
        dict = {}
        labels = []
        values = []
        bounds = []
        stochasticLabels = []
        stochasticValues = []
        stochasticBounds = []
        for param in params:
            dict[param.get_label()] = param.get_value()
            labels.append(param.get_label())
            values.append(param.get_value())
            bounds.append(param.get_bounds())
            if param.is_stochastic():
                stochasticLabels.append(param.get_label())
                stochasticValues.append(param.get_value())
                stochasticBounds.append(param.get_bounds())
        self.paramDict = dict
        self.labels = labels
        self.values = values
        self.bounds = bounds
        self.stochasticLabels = stochasticLabels
        self.stochasticValues = stochasticValues
        self.stochasticBounds = stochasticBounds

    def get(self, label):
        return self.paramDict[label]

    def get_labels(self, onlyStochastic = False):
        if onlyStochastic:
            return self.stochasticLabels
        return self.labels

    def get_values(self, onlyStochastic = False):
        if onlyStochastic:
            return self.stochasticValues
        return self.values

    def get_bounds(self, onlyStochastic = False):
        if onlyStochastic:
            return self.stochasticBounds
        return self.bounds

    def make_resampled_copy(self, staticParams = []):
        newParams = []
        for param in self.params:
            if staticParams.count(param.get_label()) > 0:
                newParam = param.make_copy()
            else:
                newParam = param.make_resampled_copy()
            newParams.append(newParam)
        return Parameters(newParams)

    def make_values_copy(self, values):
        newParams = []
        valueIt = iter(values)
        for param in self.params:
            if param.is_stochastic():
                newParam = param.make_value_copy(next(valueIt))
            else:
                newParam = param.make_copy()
            newParams.append(newParam)
        return Parameters(newParams)

class DGM:

    def __init__(self, params):
        pass

    #needs filled in

    def sample_data(self, time):
        pass

    #run simulations

    def simulate_error(self):
        r = np.random.normal(scale = self.error)
        return r

    def simulate(self, times, isStochastic = True):

        dataList = []

        for i, time in enumerate(times):
            trueData = self.sample_data(time)
            for j, datum in enumerate(trueData):
                if i == 0:
                    dataList.append([])
                if isStochastic:
                    datum *= (1 + self.simulate_error())
                dataList[j].append(datum)




        return [times, ['time'] + self.labels, dataList]

    def simulate_to_csvs(self, times, attemptCount, path, isStochastic = True):
        for i in range(1, attemptCount + 1):
            currentPath = path + str(i)
            [times, labels, dataList] = self.simulate(times, isStochastic = isStochastic)
            csv.export(times, labels, dataList, currentPath)

    #analyze data

    def compute_likelihood_function(self, error):

        if error == np.inf:
            print('bad')

        if error == np.nan:
            print('bad2')

        constant = 0.5 * math.log(2 * math.pi)
        scale = math.log(self.error)
        fact = 0.5 * (error ** 2) / (self.error ** 2)
        p = scale + fact + constant
        return p

    def get_likelihood(self, dataList, dataListExpected):


        logP = 0
        for data, exps in zip(dataList, dataListExpected):
            for datum, exp in zip(data, exps):

                if exp == 0:
                    if datum != 0:
                        logP += 1000000000000
                elif self.error == 0:
                    if exp != datum:
                        logP += 1000000000000
                else:
                    ratio = datum / exp
                    logP += self.compute_likelihood_function(ratio - 1)



        return logP

    def get_sim_likelihood(self, attemptCount, path):

        logP = 0

        for i in range(1, attemptCount + 1):
            currentPath = path + str(i)
            [times, labels, dataList] = csv.extract(currentPath)
            if i == 1:
                [_, _, dataListCompare] = self.simulate(times, isStochastic = False)
            currentLogP = self.get_likelihood(dataList, dataListCompare)
            logP += currentLogP

        return logP

    #copy

    def make_values_copy(self, values):
        newParams = self.parameters.make_values_copy(values)
        modelType = type(self)
        return modelType(newParams, self.labels)

    def make_resampled_copy(self, staticParams = []):
        newParams = self.parameters.make_resampled_copy(staticParams = staticParams)
        modelType = type(self)
        return modelType(newParams, self.labels)

    #record info

    def export(self, path, filename = 'parameters'):
        times = []
        labels = ['parameters', 'actual', 'lower bound', 'upper bound']
        lowers = []
        uppers = []
        values = []

        for param in self.parameters.params:
            times.append(param.get_label())
            values.append(param.get_value())
            (lower, upper) = param.get_bounds()
            lowers.append(lower)
            uppers.append(upper)

        dataList = [values, lowers, uppers]

        csv.export(times, labels, dataList, path + filename)

    def likelihood_to_csv(self, attemptCount, simPath, path, filename = 'likelihood'):
        likelihood = self.get_sim_likelihood(attemptCount, simPath)

        csv.export_line([likelihood], path + filename)

class HDGM(DGM):
    def __init__(self):
        pass

    def compute_population_counts(self, time):
        change = expm(self.evolutionMat * time)
        initial = np.array([self.initial]).T
        data = change @ initial

        return data.T[0]

    def sample_data(self, time):
        return self.compute_population_counts(time)

class SimpleBirth(HDGM):
    def __init__(self, params, popLabels):
        self.initial = [params.get('p')]
        self.evolutionMat = np.array([[params.get('r')]])
        self.error = params.get('error')
        self.parameters = params
        self.labels = popLabels

class PhenotypeSwitch(HDGM):
    def __init__(self, params, popLabels):

        self.parameters = params
        self.labels = popLabels

        r = params.get('r')
        l12 = params.get('l12')
        l21 = params.get('l21')
        self.evolutionMat = np.array([[r - l12, l21], [l12, r - l21]])

        self.initial = []
        self.initial.append(params.get('p1'))
        self.initial.append(params.get('p2'))

        self.error = params.get('error')

class FullInfoChip(HDGM):
    def __init__(self, params, popLabels):

        self.parameters = params
        self.labels = popLabels



        r = params.get('r')
        l12 = params.get('l12')
        l21 = params.get('l21')
        l23 = params.get('l23')


        self.evolutionMat = np.array([[r - l12, l21, 0], [l12, r - l21 - l23, 0], [0, l23, r]])

        self.initial = []
        self.initial.append(params.get('p1'))
        self.initial.append(params.get('p2'))
        self.initial.append(params.get('p3'))

        self.error = params.get('error')

class Chip(HDGM):
    def __init__(self, params, popLabels):

        self.parameters = params
        self.labels = popLabels



        r = params.get('r')
        l12 = params.get('l12')
        l21 = params.get('l21')
        l23 = params.get('l23')


        self.evolutionMat = np.array([[r - l12, l21, 0], [l12, r - l21 - l23, 0], [0, l23, r]])

        self.initial = []
        self.initial.append(params.get('p1'))
        self.initial.append(params.get('p2'))
        self.initial.append(params.get('p3'))

        self.error = params.get('error')

    def sample_data(self, time):
        popCounts = self.compute_population_counts(time)

        return [popCounts[0] + popCounts[1], popCounts[2]]

def optimize_parameters(startingModel, attemptCount, path):
    #modelType = type(startingModel)
    startingValues = startingModel.parameters.get_values(onlyStochastic = True)
    bounds = startingModel.parameters.get_bounds(onlyStochastic = True)

    def get_likelihood(values):
        model = startingModel.make_values_copy(values)
        return model.get_sim_likelihood(attemptCount, path)

    return minimize(get_likelihood, startingValues, bounds = bounds)

def fully_optimize_parameters(startingModel, startingPointCount, attemptCount, path):

    percentOn = 5
    bestParams = optimize_parameters(startingModel, attemptCount, path)
    bestF = bestParams.fun

    for i in range(1, startingPointCount + 1):

        nextModel = startingModel.make_resampled_copy()
        opt = optimize_parameters(nextModel, attemptCount, path)
        f = opt.fun
        if f < bestF:
            bestParams = opt
            bestF = f

        elif f == bestF:
            print('equaled the best result')

        if i == startingPointCount * percentOn // 100:
            print(str(percentOn) + '% complete (' + str(i) + ' optimizations completed)')
            percentOn += 5



    return bestParams

def get_distance(model1, model2):
    d = 0
    count = 0
    for [p1, p2] in zip(model1.parameters.get_values(), model2.parameters.get_values()):
        count += 1
        d += (1 - (p2 / p1)) ** 2
    d = (d / count) ** 0.5
    return d

def test_recovery(trueModel, times, attemptCount, startingPointCount, path):

    trueModel.simulate_to_csvs(times, attemptCount, path)
    trueError = trueModel.get_sim_likelihood(attemptCount, path)
    startingModel = trueModel.make_resampled_copy()
    bestParams = fully_optimize_parameters(startingModel, startingPointCount, attemptCount, path)
    bestError = bestParams.fun

    if bestError <= trueError:
        passed = True
    else:
        passed = False
    errorDiff = bestError - trueError


    bestModel = trueModel.make_values_copy(bestParams.x)
    modelDist = get_distance(trueModel, bestModel)

    return [passed, errorDiff, modelDist]

def get_starting_and_ending(dataList):
    A = []
    B = []
    popCount = len(dataList)

    for data in dataList:
        nextA = []
        nextB = []

        for j, datum in enumerate(data):
            if j < popCount:
                nextA.append(datum)
            if j > 0:
                nextB.append(datum)
        A.append(nextA)
        B.append(nextB)
    return (A, B)

def get_cellTrans(dataList, timeStep = 2):

    (A, B) = get_starting_and_ending(dataList)
    A, B = np.array(A), np.array(B)

    T = np.matmul(B, inv(A))

    Q = logm(T) / timeStep
    return Q

def get_transcompp(attemptCount, path):



    for i in range(1, attemptCount + 1):
        currentPath = path + str(i)
        [times, labels, dataList] = csv.extract(currentPath)
        timeStep = times[1] - times[0]

        if i == 1:
            Q = get_cellTrans(dataList, timeStep = timeStep)
        else:
            Q = Q + get_cellTrans(dataList, timeStep = timeStep)

    Q = np.divide(Q, attemptCount)

    return Q

def get_best_fit(startingPoints, endingPoints):
    startingPoints = np.array(startingPoints)
    endingPoints = np.array(endingPoints)

    T = endingPoints @ startingPoints.T @ inv(startingPoints @ startingPoints.T)
    return T

def test0():
    #this is to test my likelihood functions
    dataList = [[1, 2, 4]]
    dataListCompare = [[1, 2, 4]]
    params = {
    'r' : 2,
    'p' : 1,
    'error' : 1
    }
    popLabels = ['test']
    SBModel = SimpleBirth(params, popLabels)

    min = SBModel.get_likelihood(dataList, dataListCompare)


    lower = [0, 0, 0]
    upper = [2, 4, 8]

    passed = True
    for _ in range(10000):
        list = []
        for i in range(3):
            b1 = lower[i]
            b2 = upper[i]
            list.append(np.random.random() * (b2 - b1) + b1)
        likelihood = SBModel.get_likelihood(dataList, list)

        if likelihood < min:
            passed = False

    if passed:
        print('passed test 0')
    else:
        print('failed test 0')

def test1():
     #testing method of optimization


    growth = Parameter(1, 0, 10, 'r')
    initial = Parameter(10, 1, 100, 'p')
    error = Parameter(0.36787944, 0.0001, 1, 'error')

    params = Parameters([growth, initial, error])



    popLabels = ['test']
    times = [0]
    SBModel = SimpleBirth(params, popLabels)
    [_, _, dataList] = SBModel.simulate(times, isStochastic = False)

    min = SBModel.get_likelihood(dataList, dataList)
    print(min)
    """
    labels = ['r', 'p', 'error']
    lower = [0, 0, 1]
    upper = [2, 4, 1]

    currentMin = 'none'
    currentParamMin = 'none'
    for _ in range(5):
        currentParams = {}

        for i in range(3):
            param = np.random.random() * (upper[i] - lower[i]) + lower[i]
            currentParams[labels[i]] = param
        testModel = SimpleBirth(currentParams, popLabels)
        [_, _, currentData] = testModel.simulate(times, isStochastic = False)
        currentP = testModel.get_likelihood(dataList, currentData)
        print(currentP)

        if currentMin == 'none':
            currentMin = currentP
            currentParamMin = currentParams
        elif currentMin > currentP:
            currentMin = currentP
            currentParamMin = currentParams


    print(currentMin)
    print(currentParams)

    bestModel = SimpleBirth(currentParams, popLabels)
    [_, _, bestModelDataList] = bestModel.simulate(times, isStochastic = False)
    likelihood = bestModel.get_likelihood(bestModelDataList, dataList)
    likelihood2 = bestModel.get_likelihood(dataList, bestModelDataList)
    print(likelihood)

    print(likelihood2)
    """

#test parameter recovery for SimpleBirth
def test2():

    #set up the situation
    trueGrowth = Parameter(1, 0, 10, 'r')
    trueInitial = Parameter(10, 1, 100, 'p')
    trueError = Parameter(0.36787944, 0.0001, 1, 'error')
    trueParams = Parameters([trueGrowth, trueInitial, trueError])
    trueModel = SimpleBirth(trueParams, ['test'])
    path = 'output_files/tests/'
    attemptCount = 10
    times = [0, 1, 2, 3, 4, 5, 6]
    trueModel.simulate_to_csvs(times, attemptCount, path)
    goal = trueModel.get_sim_likelihood(attemptCount, path)
    print('the goal function is ' + str(goal))


    growth = Parameter(5, 0, 10, 'r')
    initial = Parameter(10, 1, 100, 'p')
    error = Parameter(0.8, 0.0001, 1, 'error')

    startingParams = Parameters([growth, initial, error])

    startingModel = SimpleBirth(startingParams, ['test'])

    opt = fully_optimize_parameters(startingModel, 10, attemptCount, path)
    print(opt)

    print(type(startingModel))

#test parameter recovery for PhenotypeSwitch
def test3():

    #set up the situation
    trueGrowth = Parameter(1, 0, 5, 'r')
    trueL12 = Parameter(0.1, 0, 1, 'l12')
    trueL21 = Parameter(0.2, 0, 1, 'l21')
    trueP1 = Parameter(1000, 1000, 1000, 'p1')
    trueP2 = Parameter(100, 100, 100, 'p2')
    error = Parameter(0.1, 0.0001, 1, 'error')
    trueParams = Parameters([
    trueGrowth,
    trueL12,
    trueL21,
    trueP1,
    trueP2,
    error])
    popLabels = ['t1', 't2']
    trueModel = PhenotypeSwitch(trueParams, popLabels)
    path = 'output_files/tests/parameter_optimization/PhenotypeSwitch/'
    outputPath = path + 'results/'
    simCount = 100
    times = [0, 2, 4, 6]
    startingPointCount = 5

    """
    trueModel.simulate_to_csvs(times, simCount, path, isStochastic = True)
    """

    goal = trueModel.get_sim_likelihood(simCount, path)


    print('goal: ' + str(goal))
    startingModel = trueModel.make_resampled_copy()
    opt = fully_optimize_parameters(startingModel, startingPointCount, simCount, path)
    optimizedFun = opt.fun
    optimizedParams = opt.x

    optimizedModel = trueModel.make_values_copy(opt.x)



    trueModel.export(path, 'true params')
    trueModel.likelihood_to_csv(simCount, path, path, 'true likelihood')
    optimizedModel.export(path, 'optimized params')
    optimizedModel.likelihood_to_csv(simCount, path, path, 'optimized likelihood')



    """
    goal = trueModel.get_sim_likelihood(simCount, path)
    print('the goal function is ' + str(goal))

    startingModel = trueModel.make_resampled_copy()
    startingPointCount = 200

    opt = fully_optimize_parameters(startingModel, startingPointCount, simCount, path)
    print('the function value found is ' + str(opt.fun))
    print(opt.x)

    print(type(startingModel))
    """


def ps_recovery():
    trueGrowth = Parameter(1, 0, 5, 'r')
    trueL12 = Parameter(0.5, 0, 1, 'l12')
    trueL21 = Parameter(0.5, 0, 1, 'l21')
    trueP1 = Parameter(1000, 1000, 1000, 'p1')
    trueP2 = Parameter(100, 100, 100, 'p2')
    error = Parameter(0.1, 0.0001, 1, 'error')
    trueParams = Parameters([
    trueGrowth,
    trueL12,
    trueL21,
    trueP1,
    trueP2,
    error])
    popLabels = ['t1', 't2']
    trueModel = PhenotypeSwitch(trueParams, popLabels)
    path = 'output_files/tests/parameter_optimization/PhenotypeSwitch/recovery/'
    fileName = 'results'
    attemptCount = 10
    startingPointCount = 1
    times = [0, 2, 4, 6]
    xlabel = 'l21'
    ylabel = 'l12'


    first = 0.1
    last = 1
    count = 10
    def make_param_list(first, last, count):
        l = [num * (last - first) / (count - 1) + first for num in range(count)]
        return l

    l12s = make_param_list(first, last, attemptCount)
    l21s = make_param_list(first, last, attemptCount)

    dataList = []
    for l12 in l12s:
        data = []
        for l21 in l21s:
            myL12 = trueL12.make_value_copy(l12)
            myL21 = trueL21.make_value_copy(l21)
            currentParams = trueParams = Parameters([
            trueGrowth,
            myL12,
            myL21,
            trueP1,
            trueP2,
            error])
            currentModel = PhenotypeSwitch(trueParams, popLabels)

            ans = test_recovery(currentModel, times, attemptCount, startingPointCount, path)
            print(ans)
            data.append(ans[2])
        dataList.append(data)

    print(dataList)
    visual_handler.make_square_plot(l21s, l12s, xlabel, ylabel, dataList, path + fileName)
#test parameter recovery for FullInfoChip

def fic_recovery():
    #set up the situation
    trueGrowth = Parameter(1, 0, 10, 'r')
    trueL12 = Parameter(0.1, 0, 1, 'l12')
    trueL21 = Parameter(0.2, 0, 1, 'l21')
    trueL23 = Parameter(0.3, 0, 1, 'l23')
    trueP1 = Parameter(1000, 1000, 1000, 'p1')
    trueP2 = Parameter(0, 0, 0, 'p2')
    trueP3 = Parameter(0, 0, 0, 'p3')
    error = Parameter(0.1, 0.000001, 1, 'error')
    trueParams = Parameters([
    trueGrowth,
    trueL12,
    trueL21,
    trueL23,
    trueP1,
    trueP2,
    trueP3,
    error])
    popLabels = ['p1', 'p2', 'p3']
    trueModel = FullInfoChip(trueParams, popLabels)
    startingModel = trueModel.make_resampled_copy()
    path = 'output_files/tests/'
    attemptCount = 10000
    times = [0, 2, 4, 6]
    startingPointCount = 500

    trueModel.simulate_to_csvs(times, attemptCount, path, isStochastic = True)

    Q = get_transcompp(attemptCount, path)
    print(Q)
    print(Q.real)





    """
    goal = trueModel.get_sim_likelihood(attemptCount, path)
    print('the goal function value is ' + str(goal))



    opt = fully_optimize_parameters(startingModel, startingPointCount, attemptCount, path)
    print('the minimal function value found is ' + str(opt.fun) + ' using the following parameters:')
    print(opt.x)
    """

def test_cellTrans():
    dataList = [[1, 0, 0, 1], [0,1,0,1], [0,0,1,1]]
    timeStep = 2
    Q1 = get_cellTrans(dataList, timeStep = timeStep)
    (startingPoints, endingPoints) = get_starting_and_ending(dataList)
    Q2 = get_best_fit(startingPoints, endingPoints)
    Q2 = 0.5 * logm(Q2)


    print("using cellTrans: " + str(Q1))
    print("using best fit: " + str(Q2))

def test_best_fit():
    startingData = [[1, 0, 0], [0, 1, 1]]
    endingData = [[2, 0, 0], [2, 2, 2]]

    T = get_best_fit(startingData, endingData)
    print(T)

def bio_data_transcompp():
    path = 'output_files/bio_data/D0-D6 Stretched/'
    attemptCount = 4

    get_transcompp(attemptCount, path)





if __name__ == "__main__":
    #fic_recovery()
    #test_best_fit()
    test_cellTrans()

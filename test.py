import matplotlib.pyplot as plt
import numpy as np
import model
import crc_models as cm
import graph as g
import simulate
import copy

def main():


    birthRate = 1.3
    deathRate = 1
    growToGoRate = 0.1
    goToGoneRate = 0.1
    peristalsisModifiers = [0, 0.05, 0.2]
    startingGrow = 1000
    startingGo = 0
    startingGone = 0
    swapTimes = [2, 4]
    duration = 6
    dataCount = 1000
    averageDataCount = 3
    attemptCount = 100


    models = []

    for peristalsisModifier in peristalsisModifiers:
        models.append(cm.InheritablePeristalsis(birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone))
        models.append(cm.NonInheritablePeristalsis(birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone))


    modelsToSim = []

    for model in models:
        modelsToSim.append(copy.deepcopy(model))




    labels = ['inheritable1', 'noninheritable1']

    for i, model in enumerate(modelsToSim):
        model.run(duration, swapTimes, dataCount)
        model.save_history_graph('output_files/test_files/' + 'example_simulation_' + str(i))

    for i, model in enumerate(models):
        simulate.make_averages(model, duration, swapTimes, attemptCount, averageDataCount, path = 'output_files/test_files/' + 'average_simulation_' + str(i))



def second():
    birthRate = 1.15
    deathRate = 1
    growToGoRate = 0.1
    goToGoneRate = 0.1
    peristalsisModifier = 0.1
    startingGrow = 1000
    startingGo = 0
    startingGone = 0
    swapTimes = [2, 4, 6]
    duration = 8



    crc = cm.SimplestModel(birthRate, deathRate, growToGoRate, goToGoneRate, startingGrow, startingGo, startingGone)
    crc.run(duration, dataCount = 5)
    #crc.save_history_graph('output_files/peristalsis')
    crc.make_history_graph()
    crc.show_history_graph()

if __name__ == "__main__":
    main()

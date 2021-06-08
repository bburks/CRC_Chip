import model
import matplotlib.pyplot as plt

#in this model, we have three types of cells - "go" "grow" and "gone"
#all have the same birthrate and same deathrate


class SimplestModel(model.Model):
    def __init__(self, birthrate, deathrate, growToGoRate, goToGoneRate, startingGrow, startingGo, startingGone):

        growPop = model.Population(startingGrow, label='grow')
        goPop = model.Population(startingGo, label='go')
        gonePop = model.Population(startingGone, label='gone')

        pops = [growPop, goPop, gonePop]

        events = []
        for pop in pops:
            events.append(model.SimpleBirth(pop, birthrate))
            events.append(model.SimpleDeath(pop, deathrate))

        growToGo = model.SimpleTransfer(growPop, goPop, growToGoRate)
        goToGone = model.SimpleTransfer(goPop, gonePop, goToGoneRate)

        events.append(growToGo)
        events.append(goToGone)


        self = super().__init__(pops, events)


#in this model, go cells give birth to grow cells instead of to go cells
class SimplestModelAlternate(model.Model):

    def __init__(self, birthRate, deathRate, growToGoRate, goToGoneRate, startingGrow, startingGo, startingGone, peristalsisAdjustment = 0):

        growPop = model.Population(startingGrow, label='grow')
        goPop = model.Population(startingGo, label='go')
        gonePop = model.Population(startingGone, label='gone')

        pops = [growPop, goPop, gonePop]
        events = []
        for pop in pops:
            events.append(model.SimpleBirth(pop, birthRate))
            events.append(model.SimpleDeath(pop, deathRate))


        growToGo = model.SimpleTransfer(growPop, goPop, growToGoRate)
        goToGone = model.SimpleTransfer(goPop, gonePop, goToGoneRate)

        events.append(growToGo)
        events.append(goToGone)

        self = super().__init__(pops, events)


class InheritablePeristalsis(model.Model):

    def __init__(self, birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone):

        growPop = model.Population(startingGrow, label='grow')
        goPop = model.Population(startingGo, label='go')
        gonePop = model.Population(startingGone, label='gone')

        pops = [growPop, goPop, gonePop]
        events = []

        growToGo = model.SimpleToggleTransfer(growPop, goPop, growToGoRate,
            growToGoRate + peristalsisModifier)
        goToGone = model.SimpleTransfer(goPop, gonePop, goToGoneRate)

        events.append(growToGo)
        events.append(goToGone)

        for pop in pops:
            events.append(model.SimpleBirth(pop, birthRate))
            events.append(model.SimpleDeath(pop, deathRate))

        self = super().__init__(pops, events)

    def toggle(self):
        self.events[0].toggle()

    def interval_run(self, swapTimes, historyTimes, duration):

        swapInc = 0
        historyInc = 0
        currentTime = 0



        while swapInc < len(swapTimes):

            if swapTimes[swapInc] > historyTimes[historyInc]:
                nextTime = historyTimes[historyInc]
                historyInc += 1
                self.empty_run(nextTime - currentTime)
            else:
                nextTime = swapTimes[swapInc]
                swapInc += 1
                self.stealth_run(nextTime - currentTime)
                self.toggle()

            currentTime = nextTime

        while historyInc < len(historyTimes):
            nextTime = historyTimes[historyInc]
            historyInc += 1
            self.empty_run(nextTime - currentTime)
            currentTime = nextTime

        if duration > currentTime:
            self.empty_run(duration - currentTime)

    def run(self, duration, swapTimes, dataCount = 1000):

        historyTimes = []
        for data in range(1, dataCount):
            historyTimes.append(data * duration / dataCount)
        historyTimes.append(duration)
        self.interval_run(swapTimes, historyTimes, duration)

class NonInheritablePeristalsis(model.Model):

    def __init__(self, birthRate, deathRate, growToGoRate, goToGoneRate, peristalsisModifier, startingGrow, startingGo, startingGone):

        growPop = model.Population(startingGrow, label='grow')
        goPop = model.Population(startingGo, label='go')
        gonePop = model.Population(startingGone, label='gone')

        pops = [growPop, goPop, gonePop]
        events = []

        growToGo = model.SimpleToggleTransfer(growPop, goPop, growToGoRate,
            growToGoRate + peristalsisModifier)
        goToGone = model.SimpleTransfer(goPop, gonePop, goToGoneRate)

        events.append(growToGo)
        events.append(goToGone)

        for pop in pops:
            if pop == goPop:
                events.append(model.SimpleNoninheritableBirth(goPop, growPop, birthRate))
            else:
                events.append(model.SimpleBirth(pop, birthRate))


            events.append(model.SimpleDeath(pop, deathRate))

        self = super().__init__(pops, events)


    def toggle(self):
        self.events[0].toggle()

    def interval_run(self, swapTimes, historyTimes, duration):

        swapInc = 0
        historyInc = 0
        currentTime = 0



        while swapInc < len(swapTimes):

            if swapTimes[swapInc] > historyTimes[historyInc]:
                nextTime = historyTimes[historyInc]
                historyInc += 1
                self.empty_run(nextTime - currentTime)
            else:
                nextTime = swapTimes[swapInc]
                swapInc += 1
                self.stealth_run(nextTime - currentTime)
                self.toggle()

            currentTime = nextTime

        while historyInc < len(historyTimes):
            nextTime = historyTimes[historyInc]
            historyInc += 1
            self.empty_run(nextTime - currentTime)
            currentTime = nextTime

        if duration > currentTime:
            self.empty_run(duration - currentTime)

    def run(self, duration, swapTimes, dataCount = 1000):

        historyTimes = []
        for data in range(1, dataCount):
            historyTimes.append(data * duration / dataCount)
        historyTimes.append(duration)
        self.interval_run(swapTimes, historyTimes, duration)


    pass

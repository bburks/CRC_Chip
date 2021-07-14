import model

# in this model, we have three types of cells - "go" "grow" and "gone".
# all have the same birthrate and same deathrate.

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


        self = super().__init__(pops, events, name = 'SimplestModel')

# in this model, go cells give birth to one go cell and one grow cell instead of to two go cells.

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

        self = super().__init__(pops, events, name = 'SimplestModelAlternate')

# now we incorporate stretching into each model to get these two models.

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

# it turns out from the data, the birthrate decreases over time.
# This event encapsulates that idea by changing the birthrate once
# the population size reaches a certain value.

class LogisticToggleBirth(model.Event):

    def __init__(self, parentPop, childPop, logisticPops, rateHigh, rateLow, popSwitchCount):
        super().__init__([childPop], [1])
        self.parentPop = parentPop
        self.childPop = childPop
        self.logisticPops = logisticPops
        self.rateHigh = rateHigh
        self.rateLow = rateLow
        self.popSwitchCount = popSwitchCount

    def get_rate(self):
        logisticPopCount = 0
        for pop in self.logisticPops:
            logisticPopCount += pop.get_size()

        if logisticPopCount > self.popSwitchCount:
            proRate = self.rateLow
        else:
            proRate = self.rateHigh

        return proRate * self.parentPop.get_size()

# here's an unrealistic model used to test that logisic births work.

class TwoPopLogistic(model.ToggleModel):

    def __init__(self, params):
        birthRateHigh = params.get('higher birthrate')
        birthRateLow = params.get('lower birthrate')
        swapCount = params.get('birthrate swaps at')
        deathRate = params.get('deathrate')
        transferDefaultRate = params.get('go to gone')
        transferPeristalsisRate = params.get('go to gone peristalsis')
        startingGrow = params.get('starting go')
        startingGone = params.get('starting gone')


        growPop = model.Population(startingGrow, label = 'top')
        gonePop = model.Population(startingGone, label = 'bottom')

        pops = [growPop, gonePop]
        events = []
        for pop in pops:
            death = model.SimpleDeath(pop, deathRate)
            birth = LogisticToggleBirth(pop, pop, [pop], birthRateHigh, birthRateLow, swapCount)

            events.append(death)
            events.append(birth)

        intravasation = model.SimpleToggleTransfer(growPop, gonePop, transferDefaultRate, transferPeristalsisRate)
        events.append(intravasation)

        super().__init__(pops, events, [intravasation], name = 'TwoPopLogistic')

# here's our two original 'simplest' models, now incorporating logisitic births.

class ThreePopLogisticNonInheritable(model.ToggleModel):
    def __init__(self, params):

        birthRateHigh = params.get('higher birthrate')
        birthRateLow = params.get('lower birthrate')
        swapCount = params.get('birthrate swaps at')

        deathRate = params.get('deathrate')

        transferDefaultRate = params.get('grow to go')
        transferPeristalsisRate = params.get('grow to go peristalsis')
        intravasationRate = params.get('go to gone')

        startingGrow = params.get('starting grow')
        startingGo = params.get('starting go')
        startingGone = params.get('starting gone')


        growPop = model.Population(startingGrow, label = 'grow')
        goPop = model.Population(startingGo, label = 'go')
        gonePop = model.Population(startingGone, label = 'gone')

        pops = [growPop, goPop, gonePop]

        events = []
        for pop in pops:
            death = model.SimpleDeath(pop, deathRate)
            if pop == gonePop:
                birth = LogisticToggleBirth(pop, pop, [gonePop], birthRateHigh, birthRateLow, swapCount)
            else:
                birth = LogisticToggleBirth(pop, growPop, [growPop, goPop], birthRateHigh, birthRateLow, swapCount)
            events.extend([birth, death])

        growToGo = model.SimpleToggleTransfer(growPop, goPop, transferDefaultRate, transferPeristalsisRate)
        goToGone = model.SimpleTransfer(goPop, gonePop, intravasationRate)
        events.extend([growToGo, goToGone])

        super().__init__(pops, events, [growToGo], name = 'ThreePopLogisticNonInheritable')

class ThreePopLogisticInheritable(model.ToggleModel):
    def __init__(self, params):

        birthRateHigh = params.get('higher birthrate')
        birthRateLow = params.get('lower birthrate')
        swapCount = params.get('birthrate swaps at')

        deathRate = params.get('deathrate')

        transferDefaultRate = params.get('grow to go')
        transferPeristalsisRate = params.get('grow to go peristalsis')
        intravasationRate = params.get('go to gone')

        startingGrow = params.get('starting grow')
        startingGo = params.get('starting go')
        startingGone = params.get('starting gone')


        growPop = model.Population(startingGrow, label = 'grow')
        goPop = model.Population(startingGo, label = 'go')
        gonePop = model.Population(startingGone, label = 'gone')

        pops = [growPop, goPop, gonePop]

        events = []
        for pop in pops:
            death = model.SimpleDeath(pop, deathRate)
            if pop == gonePop:
                birth = LogisticToggleBirth(pop, pop, [gonePop], birthRateHigh, birthRateLow, swapCount)
            else:
                birth = LogisticToggleBirth(pop, pop, [growPop, goPop], birthRateHigh, birthRateLow, swapCount)
            events.extend([birth, death])

        growToGo = model.SimpleToggleTransfer(growPop, goPop, transferDefaultRate, transferPeristalsisRate)
        goToGone = model.SimpleTransfer(goPop, gonePop, intravasationRate)
        events.extend([growToGo, goToGone])

        super().__init__(pops, events, [growToGo], name = 'ThreePopLogisticInheritable')

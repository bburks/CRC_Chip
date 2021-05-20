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



class BasicPeristalsis(model.Model):

    def __init__(self,
            birthRate,
            deathRate,
            growToGoRate,
            goToGoneRate,
            peristalsisModifier,
            startingGrow,
            startingGo,
            startingGone,
            ):

        growPop = model.Population(startingGrow, label='grow')
        goPop = model.Population(startingGo, label='go')
        gonePop = model.Population(startingGone, label='gone')

        pops = [growPop, goPop, gonePop]
        events = []

        for pop in pops:
            events.append(model.SimpleBirth(pop, birthRate))
            events.append(model.SimpleDeath(pop, deathRate))

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

    def __init__(self, birthrate, deathrate, growToGoRate, goToGoneRate, startingGrow, startingGo, startingGone):

        growPop = model.Population(startingGrow)
        goPop = model.Population(startingGo)
        gonePop = model.Population(startingGone)


        growBirth = model.Event([growPop], [1], birthrate)
        goBirth = model.Event([growPop], [1], birthrate)
        goneBirth = model.Event([gonePop], [1], birthrate)

        growDeath = model.Event([growPop], [-1], deathrate)
        goDeath = model.Event([goPop], [-1], deathrate)
        goneDeath = model.Event([gonePop], [-1], deathrate)

        growToGo = model.Event([growPop, goPop], [-1, 1], growToGoRate)
        goToGone = model.Event([goPop, gonePop], [-1, 1], goToGoneRate)


        growPop.add_event(growBirth)
        growPop.add_event(growDeath)
        growPop.add_event(growToGo)

        goPop.add_event(goBirth)
        goPop.add_event(goDeath)
        goPop.add_event(goToGone)

        gonePop.add_event(goneBirth)
        gonePop.add_event(goneDeath)

        self = super().__init__([growPop, goPop, gonePop])

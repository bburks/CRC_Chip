import model

#in this model, we have three types of cells - "go" "grow" and "gone"
#all have the same birthrate and same deathrate


class SimplestModel(model.Model):
    def __init__(self, birthrate, deathrate, growToGoRate, goToGoneRate, startingGrow, startingGo, startingGone):

        growPop = model.Population(startingGrow)
        goPop = model.Population(startingGo)
        gonePop = model.Population(startingGone)


        growBirth = model.Event([growPop], [1], birthrate)
        goBirth = model.Event([goPop], [1], birthrate)
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

    pass







def main():
    import matplotlib.pyplot as plt

    crc = SimplestModel(1, 0.9, 0.1, 0.01, 100, 0, 0)
    maxTime = 20



    timeData = []
    goData = []
    growData = []
    goneData = []

    while crc.get_time() < maxTime:
        timeData.append(crc.get_time())
        growData.append(crc.get_population(0).get_size())
        goData.append(crc.get_population(1).get_size())
        goneData.append(crc.get_population(2).get_size())

        if crc.get_total_rate() == 0:
            print('populations all extinct')
            break

        crc.update()








    growFigure, growAx = plt.subplots()
    growAx.plot(timeData, growData, label = 'grow')

    growAx.plot(timeData, goData, label = 'go')
    growAx.plot(timeData, goneData, label = 'gone')
    growAx.legend()

    plt.show()
if __name__ == "__main__":
    main()

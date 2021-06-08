import random
import math
import matplotlib.pyplot as plt
import graph
"""When implementing a model, first create populations, then create events.
Combine populations and events into a model.

You cannot use events on their own; they need to be implemented be subclasses
that define a rate function.

-SimpleEvent is a subclass where the rate is proportional to the
size of some population.
-SimpleBirth increases the population
-SimpleDeath decreases the populations
-SimpleTransfer keeps population sizes the same on net -- one population
increases by one while another decreases by one.
-SimpleToggleEvent and SimpleToggleTransfer include a possibility that the rate
could change over time
"""



class Population:

    # a population can be thought of all cells of a type. has a size
    #(number of cells) and possible events (e.g., birth, death, transition)

    def __init__(self, count, label = ''):
        self.count = count
        self.history = []
        self.label = label

    def get_size(self):
        return self.count

    def add_size(self, inc):
        self.count += inc

    def set_size(self, count):
        self.count = count

    def get_history(self):
        return self.history

    def update_history(self):
        self.history.append(self.get_size())

    def set_history(self, hist):
        self.history = hist #beware using this


class Event:

    # an event is something that happens -- a birth, a death, a cell type
    # change are all examples

    def __init__(self, populations, changes):
        self.populations = populations
        self.changes = changes

    def implement(self):

        for i, pop in enumerate(self.populations):
            pop.add_size(self.changes[i])

    def get_rate(self):
        pass

class Model:

    # a model combines populations and events with their history and can run
    # a stochastic simulation

    # constructor - Models contain populations, a current time, and a history
    # of their past.

    def __init__(self, pops, events):

        self.populations = pops
        self.events = events
        self.time = 0
        self.timeHistory = []
        self.update_history()



    #informative functions

    def get_time(self):
        return self.time

    def get_time_history(self):
        return self.timeHistory

    def get_events(self):
        return self.events

    def get_populations(self):
        return self.populations

    def get_total_rate(self):
        totalRate = 0
        for event in self.get_events():
            totalRate += event.get_rate()
        return totalRate;



    # functions for changing/creating the model:

    def add_population(self, pop):
    # this will eventually be fixed by putting history in population.
        self.populations.append(pop)

    def set_time(self, newTime):
        self.time = newTime

    def increment_time(self, inc):
        self.time += inc

    def add_event(self, event):
        self.events.append(event)

    def update_time_history(self):
        self.get_time_history().append(self.get_time())

    def update_population_history(self):
        for pop in self.get_populations():
            pop.update_history()

    def update_history(self):
        self.update_time_history()
        self.update_population_history()

    # functions involving randomness:

    def get_waiting_time(self):
        r = random.random()
        return  math.log(r) * (-1) / self.get_total_rate()

    def get_random_event(self):

        r = random.random()*self.get_total_rate()


        for currentEvent in self.get_events():
            currentRate = currentEvent.get_rate()
            if r <= currentRate:
                return currentEvent
            r -= currentRate

    # functions for updating the model:

    def update_time(self):
        self.increment_time(self.get_waiting_time())

    def update_populations(self):
        event = self.get_random_event()
        event.implement()

    def update(self):
        self.update_time_history()
        self.update_population_history()
        self.update_time()
        self.update_populations()

    def stealth_run(self, duration):



        endingTime = self.get_time() + duration

        while True:

            if self.get_total_rate() == 0:
                break

            self.update_time()

            if self.get_time() > endingTime:
                break

            self.update_populations()

        self.set_time(endingTime)

    def empty_run(self, duration):

        self.stealth_run(duration)
        self.update_history()

    def interval_run(self, historyTimes):
        historyTimes.sort() #might need a shallow copy depending on usage
        lastTime = 0
        for time in historyTimes:
            self.empty_run(time - lastTime)
            lastTime = time

    def run(self, duration, dataCount = 1000):

        historyTimes = []
        for data in range(1, dataCount):
            historyTimes.append(data * duration / dataCount)
        historyTimes.append(duration) #outside the loop to ensure final time
        #does not have a floating point issue


        self.interval_run(historyTimes)

    # functions for results analysis

    def make_history_graph(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("population growth over time")
        self.ax.set_xlabel("time")
        self.ax.set_ylabel("population count")


        for pop in self.get_populations():
            self.ax.plot(
            self.get_time_history(),
            pop.get_history(),
            label = pop.label
            )  # Plot some data on the axes.

        self.ax.legend()

    def show_history_graph(self):
        plt.show()

    def save_history_graph(self, filename, graphName = ''):
         #self.fig.savefig(filename, transparent=False, dpi=160, bbox_inches="tight")
         xdata = self.get_time_history()
         ydatas = []
         labels = []
         for pop in self.get_populations():
             ydatas.append(pop.get_history())
             labels.append(pop.label)

         g = graph.Graph(xdata, ydatas, labels, xlabel = 'time', ylabel = 'population count', name = graphName)
         g.save_graph(filename)

    def save_log_history_graph(self, filename, graphName = ''):

        xdata = self.get_time_history()
        ydatas = []
        labels = []
        for pop in self.get_populations():
            ydatas.append(pop.get_history())
            labels.append(pop.label)

        g = graph.Graph(xdata, ydatas, labels, xlabel = 'time', ylabel = 'population count', name = graphName)
        g.save_log_graph(filename)

    # beware using these

    def set_time_history(self, hist):
        self.history = hist

class SimpleEvent(Event):
    def __init__(self, populations, changes, rate, proPop):
        super().__init__(populations, changes)
        self.proportionalPop = proPop
        self.rate = rate

    def get_rate(self):
        return self.rate * self.proportionalPop.get_size()

    def set_rate(self, newRate):
        self.rate = newRate

class SimpleBirth(SimpleEvent):
    def __init__(self, birthPop, birthRate):
        self = super().__init__([birthPop], [1], birthRate, birthPop)

class SimpleDeath(SimpleEvent):
    def __init__(self, deathPop, deathRate):
        self = super().__init__([deathPop], [-1], deathRate, deathPop)

class SimpleTransfer(SimpleEvent):
    def __init__(self, fromPop, toPop, transferRate):
        self = super().__init__([fromPop, toPop], [-1, 1], transferRate, fromPop)

class SimpleNoninheritableBirth(SimpleEvent):
    def __init__(self, parentPop, childPop, birthRate):
        self = super().__init__([childPop], [1], birthRate, parentPop)

class SimpleToggleEvent(SimpleEvent):
    def __init__(self, populations, changes, startingRate, toggledRate, proPop):
        super().__init__(populations, changes, startingRate, proPop)
        self.rate1 = startingRate
        self.rate2 = toggledRate
        self.toggled = False

    def toggle(self):
            if self.toggled:
                self.toggled = False
            else:
                self.toggled = True

    def get_rate(self):
        if self.toggled:
            return self.rate2 * self.proportionalPop.get_size()
        else:
            return self.rate1 * self.proportionalPop.get_size()

class SimpleToggleTransfer(SimpleToggleEvent):
        def __init__(self, fromPop, toPop, startingRate, toggledRate):
            self = super().__init__([fromPop, toPop], [-1, 1], startingRate, toggledRate, fromPop)

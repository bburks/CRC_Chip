import random
import math
import matplotlib.pyplot as plt
import graph
import csv
import copy




"""When implementing a model, first create populations, then create events.
Combine populations and events into a model.

You cannot use events on their own; they need to be implemented by subclasses
that define a get_rate(self) method.

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

    # a population can be thought of as all cells of a specific type.
    # has a size (number of cells) and possible events
    # (e.g., birth, death, transition)

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

    def get_label(self):
        return self.label

    def set_label(self, label):
        self.label = label

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

    def __init__(self, pops, events, name = 'model'):

        self.populations = pops
        self.events = events
        self.name = name
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

    def add_event(self, event):
        self.events.append(event)

    def set_time(self, newTime):
        self.time = newTime

    def increment_time(self, inc):
        self.time += inc

    # update_history is the only one we'll want to call. it is bad to update
    # time history without updating population histories, and vice versa

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
        lastTime = 0
        for time in historyTimes:
            self.empty_run(time - lastTime)
            lastTime = time

    @staticmethod
    def make_intervals(duration, dataCount):
        historyTimes = []
        for data in range(1, dataCount):
            historyTimes.append(data * duration / dataCount)
        historyTimes.append(duration)
        return historyTimes

    def run(self, duration, dataCount = 1000):

        historyTimes = make_intervals(duration, dataCount)

        self.interval_run(historyTimes)

    # functions for results analysis - all are useless at this point

    def make_history_graph(self, graphName = ''):
        #self.fig.savefig(filename, transparent=False, dpi=160, bbox_inches="tight")
        xdata = self.get_time_history()
        ydatas = []
        labels = []
        errors = []
        for pop in self.get_populations():
            ydatas.append(pop.get_history())
            labels.append(pop.label)
            errors.append(0)

        g = graph.Graph(xdata, ydatas, errors, labels, xlabel = 'time', ylabel = 'population count', name = graphName)
        return g

    def save_history_graph(self, path, graphName = ''):
         g = make_history_graph(graphName = graphName)
         g.save_no_errors_graph(path)

    def save_log_history_graph(self, path, graphName = ''):
        g = make_history_graph(graphName = graphName)
        g.save_log_graph(path)

    def export_to_csv(self, path):
        with open(path + '.csv', 'w', newline='') as csvfile:
            csvWriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)

            csvWriter.writerow(['time'] + self.get_time_history())

            for pop in self.get_populations():
                csvWriter.writerow([pop.label] + pop.get_history())



class ToggleModel(Model):
    def __init__(self, pops, events, toggleEvents, name = 'ToggleModel'):
        super().__init__(pops, events, name)
        self.toggleEvents = toggleEvents


    def toggle(self):
        for event in self.toggleEvents:
            event.toggle()

    def is_toggled(self):
        return self.get_events()[0].is_toggled()

    @staticmethod
    def combineLists(historyTimes, toggleTimes):


        len1 = len(historyTimes)
        len2 = len(toggleTimes)



        combined = []
        isAToggles = []

        i, j = 0, 0

        while i < len1 and j < len2:
            if historyTimes[i] < toggleTimes[j]:
                combined.append(historyTimes[i])
                isAToggles.append(False)
                i += 1
            else:
                combined.append(toggleTimes[j])
                isAToggles.append(True)
                j += 1

        combined = combined + historyTimes[i:] + toggleTimes[j:]
        isAToggles = isAToggles  + [False] * (len1 - i) + [True] * (len2 - j)

        return [combined, isAToggles]

    @staticmethod
    def make_intervals(duration, dataCount):
        intervals = []
        for i in range(1, dataCount):
            intervals.append(i * duration / dataCount)
        intervals.append(duration)
        return intervals

    def run(self, duration, dataCount = 1000, toggleTimes = []):

        historyTimes = ToggleModel.make_intervals(duration, dataCount)
        [intervalTimes, isAToggles] = ToggleModel.combineLists(historyTimes, toggleTimes)
        self.interval_run(intervalTimes, isAToggles)

    def interval_run(self, intervalTimes, isAToggles):
        print('starting simulation')
        print(intervalTimes)

        intervalCount = len(intervalTimes)
        lastTime = 0


        for i, time in enumerate(intervalTimes):
            duration = time - lastTime

            if isAToggles[i]:
                self.stealth_run(duration)
                self.toggle()
            else:
                self.empty_run(duration)

            lastTime = time
        print('ending simulation')

class SimpleEvent(Event):
    def __init__(self, populations, changes, rate, proportionalPop):
        super().__init__(populations, changes)
        self.proportionalPop = proportionalPop
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

    def is_toggled(self):
        return self.toggled

    def get_rate(self):
        if self.toggled:
            return self.rate2 * self.proportionalPop.get_size()
        else:
            return self.rate1 * self.proportionalPop.get_size()

class SimpleToggleTransfer(SimpleToggleEvent):
        def __init__(self, fromPop, toPop, startingRate, toggledRate):
            self = super().__init__([fromPop, toPop], [-1, 1], startingRate, toggledRate, fromPop)

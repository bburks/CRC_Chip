import random
import math

# when implementing a model, first create populations, then create events.
# then add events to populations, combine populations into model.


# TODO: move history from model to population. time history will be stored in
# the model while population history will be stored in population. I forget why
# I want that but it was important to me at some point for some reason.

class Population:

    # a population is a cell type. has a size (number of cells) and possible
    # events (birth, death, transition)

    def __init__(self, count):
        self.count = count
        self.events = []
    def get_size(self):
        return self.count
    def add_population(self, inc):
        self.count += inc
    def set_size(self, count):
        self.count = count
    def get_total_rate(self):

        rate = 0
        for event in self.events:
            rate += event.get_rate()
        return rate*self.get_size()
    def get_number_of_events(self):
        return let(self.events)
    def get_event(self, eventNumber):
        return self.events[eventNumber]
    def add_event(self, event):
        self.events.append(event)

class Event:

    # an event is something that happens -- a birth, a death, a cell type
    # change are all examples
    def __init__(self, populations, changes, rate):
        self.populations = populations
        self.changes = changes
        self.rate = rate

    def implement(self):

        for i in range(0, len(self.populations)):
            self.populations[i].add_population(self.changes[i])

    def get_rate(self):
        return self.rate

class Model:
    # a model combines populations and events with their history and can run
    # a stochastic simulation

    # constructor - Models contain populations, a current time, and a history
    # of their past.

    def __init__(self, pops):

        self.populations = pops
        self.time = 0
        self.history = []
        for i in range(0, len(pops) + 1):
            self.history.append([])


    #informative functions:
    def get_population(self, i):
        return self.populations[i]
    def get_time(self):
        return self.time
    def get_history(self):
        return self.history

    def get_number_of_populations(self):
        return len(self.populations)
    def get_total_rate(self):
        total = 0
        for pop in self.populations:
            total += pop.get_total_rate()
        return total;



    # functions for changing/creating the model:
    def add_population(self, pop): # currently broken because no history!
    # this will eventually be fixed by putting history in population.
        self.populations.append(pop)





    # functions for updating the model:
    def get_waiting_time(self):
        r = random.random()
        return math.log(r) * (-1) / self.get_total_rate()


    def update_history(self):


        self.history[0].append(self.get_time())
        for i in range(0, self.get_number_of_populations()):
            self.history[i + 1].append(self.get_population(i).get_size())
    def update(self):

        self.update_history()

        self.time += self.get_waiting_time()

        r = random.random()*self.get_total_rate()

        for pop in self.populations: #figure out which population has the event
            popRate = pop.get_total_rate()
            if r <= popRate:
                popWithEvent = pop
                break
            r -= popRate


        r = r / popWithEvent.get_size()

        for event in popWithEvent.events:
            if r <= event.get_rate():
                event.implement()
                return
            r -= event.get_rate()

        print("you should never see this")

    def get_random_event(self): #TODO: this will simplify update(self)
        # but is not currently necessary - just will improve readability
        pass

    def run(self, duration):


            endingTime = self.get_time() + duration

            while self.get_time() < endingTime:
                if self.get_total_rate() == 0: #extinction
                    break
                self.update()


            self.time = endingTime
            for i in range(0, self.get_number_of_populations()):
                self.get_population(i).set_size(self.history[i][-1])

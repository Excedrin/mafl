from queue import *
from action import Action
import copy

# bus swaps two player's seating assignments
# if a and b are bussed, everything that would affect a now affects b
# and vice versa

# unlike redirect,
# inspections and results that include a target's name should still have
# the actual name

class actbus(Action):
    def __init__(self, actor, targets):
        self.priority = 13
        self.actor = actor
        self.targets = targets
        self.name = "bus"

    def resolve(self, state):
        state.resolved(self)

        source = self.targets[0]
        dest = self.targets[1]

        state.players[source].bussed = dest
        state.players[dest].bussed = source

        newqueue = Queue()
        for act in state.queue:
            newtargets = []
            for target in act.targets:
                if target == source:
                    newtargets.append(dest)
                elif target == dest:
                    newtargets.append(source)
                else:
                    newtargets.append(target)
            if newtargets != act.targets:
                newact = copy.deepcopy(act)
                newact.targets = newtargets
                print("newact:",newact)
                newqueue.enqueue(newact)
            else:
                newqueue.enqueue(act)
        return newqueue

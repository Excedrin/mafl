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
        self.priority = 12
        self.actor = actor
        self.targets = targets
        self.name = "bus"

    def resolve(self, state):
        state.resolved(self)

        source = self.targets[0]
        dest = self.targets[1]

        if source in state.bus:
            state.bus[source].append(dest)
        else:
            state.bus[source] = [dest]
        if dest in state.bus:
            state.bus[dest].append(source)
        else:
            state.bus[dest] = [source]
        print("state.bus",state.bus)

        return state.queue

from queue import *
from action import Action

class actkill(Action):
    def __init__(self, actor, targets):
        self.priority = 70
        self.actor = actor
        self.targets = targets
        self.name = "kill"

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            state.players[target].living = False
            print("kill %s resolved" % target)

        return state.queue

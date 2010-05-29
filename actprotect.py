from queue import *
from action import Action
from actkill import *

class actprotect(Action):
    def __init__(self, actor, targets):
        self.priority = 50
        self.actor = actor
        self.targets = targets
        self.name = "protect"

    def resolve(self, state):
        state.target(self.actor, self.targets)

        queue = state.queue

        target = self.targets[0]

        newqueue = Queue()
        for act in queue:
            if not (isinstance(act, actkill) and target in act.targets):
                newqueue.enqueue(act)
            else:
                print("kill %s canceled by protect" % act.targets)
        return newqueue

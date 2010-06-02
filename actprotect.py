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
        state.resolved(self)

        killfound = False
        for target in self.targets:
            newqueue = Queue()
            for act in state.queue:
                if killfound or (not (isinstance(act, actkill) and target in act.targets)):
                    newqueue.enqueue(act)
                else:
                    killfound = True
#                    print("kill %s canceled by protect" % act.targets)
                    state.resolved(act)
        return newqueue

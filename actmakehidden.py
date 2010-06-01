from queue import *
from action import Action

class actmakehidden(Action):
    def __init__(self, actor, targets):
        self.priority = 11
        self.actor = actor
        self.targets = targets
        self.name = "makehidden"

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            # all actions targeting a hidden player fail
            newqueue = Queue()
            for act in state.queue:
                if act.targets[0] != target:
                    newqueue.enqueue(act)
        return newqueue

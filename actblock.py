from queue import *
from action import Action

class actblock(Action):
    def __init__(self, actor, targets):
        self.priority = 12
        self.actor = actor
        self.targets = targets
        self.name = "block"

    def resolve(self, state):
        state.target(self.actor, self.targets)

        newqueue = Queue()
        for act in state.queue:
            if not act.actor in self.targets:
                newqueue.enqueue(act)
        return newqueue

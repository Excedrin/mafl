from queue import *
from action import Action

class actblock(Action):
    def __init__(self, actor, targets):
        self.priority = 13
        self.actor = actor
        self.targets = targets
        self.name = "block"

    def resolve(self, state):
        newqueue = Queue()
 
        for act in state.queue:
            if not act.actor in state.fix(self.targets):
                newqueue.enqueue(act)
            # blocked actions don't go into resqueue

        state.resolved(self)
        return newqueue

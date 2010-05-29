from queue import *

from action import Action

from actmessage import actmessage

class actinspect(Action):
    def __init__(self, actor, targets):
        self.priority = 20
        self.actor = actor
        self.targets = targets
        self.name = "inspect"

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            state.queue.enqueue(actmessage(self.actor, [self.actor], ["%s is %s" % (target, state.players[target].align)] ))

        return state.queue

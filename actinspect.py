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
            align = state.lookup(target).faction.name

            msg = "%s is %s" % (target, align)
            state.queue.enqueue(actmessage(self.actor, [self.actor], [msg]))

        return state.queue

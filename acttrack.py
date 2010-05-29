from queue import *

from action import Action

from actmessage import actmessage

class acttrack(Action):
    def __init__(self, actor, targets):
        self.priority = 91
        self.actor = actor
        self.targets = targets
        self.name = "track"

    def resolve(self, state):
        if self.priority == 91:
            state.target(self.actor, self.targets)
            self.priority = 92
            state.queue.enqueue(self)
        else:
            for target in self.targets:
                result = state.gettargets(target)

                msg = ["%s targeted %s" % (target, result) ]
                state.queue.enqueue(actmessage(self.actor, [self.actor], msg))

        return state.queue

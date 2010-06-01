from queue import *

from action import Action

from actmessage import actmessage
from untrackable import Untrackable

class actwatch(Action):
    def __init__(self, actor, targets):
        self.priority = 90
        self.actor = actor
        self.targets = targets
        self.name = "watch"

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            realtarget = state.lookup(target).name
            acted = False
            for act in state.queue + state.resqueue:
                if not isinstance(act, Untrackable) and act.actor == realtarget:
                    acted = True
                    break

            result = "used an ability" if acted else "didn't use an ability"

            msg = "%s %s" % (target, result)

            state.queue.enqueue(actmessage(self.actor, [self.actor], [msg]))

        return state.queue

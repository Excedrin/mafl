from queue import *

from action import Action
from untrackable import Untrackable

from actmessage import actmessage

class acttrack(Action):
    def __init__(self, actor, targets):
        self.priority = 90
        self.actor = actor
        self.targets = targets
        self.name = "track"

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            realtarget = state.lookup(target).name
            acted = False
            targets = []
            for act in state.queue + state.resqueue:
                if not isinstance(act, Untrackable) and act.actor == realtarget:
                    targets.extend(act.targets)

            msg = "%s targeted %s" % (target, targets)
            state.queue.enqueue(actmessage(self.actor, [self.actor], [msg]))

        return state.queue

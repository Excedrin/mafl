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
            acted = False
            targets = []
            for act in state.queue:
                if not isinstance(act, Untrackable) and act.actor == target:
                    print("found lower priority:",act)
                    targets.extend(act.targets)
            if not acted:
                for act in state.resqueue:
                    if not isinstance(act, Untrackable) and act.actor == target:
                        print("found resolved action:",act)
                        targets.extend(act.targets)

            targetname = target
            if state.players[target].bussed:
                targetname = state.players[target].bussed

            msg = "%s targeted %s" % (targetname, targets)
            state.queue.enqueue(actmessage(self.actor, [self.actor], [msg]))

        return state.queue

from queue import *

from action import Action
from untrackable import Untrackable

from actmessage import actmessage

class actpatrol(Action):
    def __init__(self, actor, targets):
        self.priority = 90
        self.actor = actor
        self.targets = targets
        self.name = "patrol"

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            acted = False
            actors = []
            for act in state.queue:
                if not isinstance(act, Untrackable) and target in act.targets:
                    print("found lower priority:",act)
                    actors.extend(act.actor)
            if not acted:
                for act in state.resqueue:
                    if not isinstance(act, Untrackable) and target in act.targets:
                        print("found resolved action:",act)
                        actors.extend(act.actor)

            msg = ["%s was targeted by %s" % (target, actors) ]
            state.queue.enqueue(actmessage(self.actor, [self.actor], msg))

        return state.queue

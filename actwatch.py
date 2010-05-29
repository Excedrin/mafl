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
            acted = False
            for act in state.queue:
                if not isinstance(act, Untrackable) and act.actor == target:
                    print("found unresolved lower priority action:", act)
                    acted = True
                    break
            if not acted:
                for act in state.resqueue:
                    if not isinstance(act, Untrackable) and act.actor == target:
                        print("found resolved higher priority action:", act)
                        acted = True
                        break

#            result = "didn't use an ability"
            result = "used an ability" if acted else "didn't use an ability"

            state.queue.enqueue(actmessage(self.actor, [self.actor], ["%s %s" % (target, result) ] ))

        return state.queue

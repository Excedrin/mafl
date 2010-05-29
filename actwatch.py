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
        state.target(self.actor, self.targets)

        for target in self.targets:

            result = "didn't use an ability"
            if bool(state.gettargets(target)):
                result = "used an ability"
            else:
                for act in state.queue:
                    if not isinstance(act, Untrackable) and act.actor == target:
                        acted = True
                        result = "used an ability"

            state.queue.enqueue(actmessage(self.actor, [self.actor], ["%s %s" % (target, result) ] ))

        return state.queue

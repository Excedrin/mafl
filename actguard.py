from queue import *
from action import Action
from actkill import *

class actguard(Action):
    def __init__(self, actor, targets):
        self.priority = 40
        self.actor = actor
        self.targets = targets
        self.name = "guard"

    def resolve(self, state):
        state.resolved(self)

        killfound = False
        for target in self.targets:
            newqueue = Queue()
            for act in state.queue:
                if killfound or (not (isinstance(act, actkill) and target in act.targets)):
                    newqueue.enqueue(act)
                else:
                    # bodyguard kills the killer (ignore bus)
                    newqueue.enqueue(actkill(self.actor, state.lookup(act.actor).name))
                    # bodyguard dies instead of target
                    newqueue.enqueue(actkill(act.actor, self.actor))
                    killfound = True
        return newqueue

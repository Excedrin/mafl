from queue import *
from action import Action

class actimmune(Action):
    def __init__(self, actor, targets, args):
        self.priority = 8
        self.actor = actor
        self.targets = targets
        self.args = args
        self.name = "immune"

    def resolve(self, state):
        state.resolved(self)

        newqueue = Queue()
        for act in state.queue:
            for target in self.targets:
                if target in act.targets:
                    for immuneact in self.args:
                        if isinstance(act, immuneact):
#                            print("%s is immune to %s" %(target, act))
                            state.resqueue.enqueue(act)
                        else:
                            newqueue.enqueue(act)
                else:
                    newqueue.enqueue(act)

        return newqueue

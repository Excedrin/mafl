from queue import *
from action import Action
import copy

class actcopy(Action):
    def __init__(self, actor, targets):
        self.priority = 10
        self.actor = actor
        self.targets = targets
        self.name = "copy"

    def resolve(self, state):
        state.resolved(self)

        source = self.targets[0]
        dest = self.targets[1]
#        print("copy src: %s dst: %s" %(source,dest))

        newqueue = Queue()
        for act in state.queue:
            if act.actor == source:
                newact = copy.deepcopy(act)
                newact.actor = source
                newact.targets[0] = dest
#                print("newact:",newact)
                newqueue.enqueue(newact)
            newqueue.enqueue(act)
        return newqueue

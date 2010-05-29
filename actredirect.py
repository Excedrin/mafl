from queue import *
from action import Action
import copy

class actredirect(Action):
    def __init__(self, actor, targets):
        self.priority = 13
        self.actor = actor
        self.targets = targets
        self.name = "redirect"

    def resolve(self, state):
        state.target(self.actor, self.targets)

        queue = state.queue

        source = self.targets[0]
        dest = self.targets[1]

        newqueue = Queue()
        for act in queue:
            if act.actor == source:
                newact = copy.deepcopy(act)
                newact.targets[0] = dest
                print("newact:",newact)
                newqueue.enqueue(newact)
            else:
                newqueue.enqueue(act)
        return newqueue

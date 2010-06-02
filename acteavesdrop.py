from action import Action
from untrackable import Untrackable
from queue import *
from actmessage import *
import copy

class acteavesdrop(Action, Untrackable):
    def __init__(self, actor, targets):
        self.priority = 95
        self.actor = actor
        self.targets = targets
        self.name = "eavesdrop"

    def resolve(self, state):
        newqueue = Queue()
        for act in state.queue:
            for target in self.targets:
                if isinstance(act, actmessage) and target in act.targets:
                    newact = copy.deepcopy(act)
                    newact.targets = [self.actor]
                    newqueue.enqueue(newact)
            newqueue.enqueue(act)
        return newqueue

from queue import *
from action import Action

class actreflex(Action):
    def __init__(self, actor, targets, args):
        self.priority = 9
        self.actor = actor
        self.targets = targets
        self.args = args
        self.name = "reflex"

    def resolve(self, state):
        state.resolved(self)

        queue = state.queue

        for target in self.targets:
            newqueue = Queue()
            for act in queue:
                if target in act.targets:
                    for reflexact in self.args:
                        reflexact.actor = target
                        reflexact.targets = [act.actor]
                        newqueue.enqueue(reflexact)
        return newqueue

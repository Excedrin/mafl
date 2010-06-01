from queue import *
from action import Action

class actkill(Action):
    def __init__(self, actor, targets):
        self.priority = 70
        self.actor = actor
        self.targets = targets
        self.name = "kill"

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            player = state.lookup(target)
            player.living = False
            print("kill %s resolved (%s killed by %s)" % (target, player.name, self.actor))

        return state.queue

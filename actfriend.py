from queue import *

from action import Action

from actmessage import actmessage

class actfriend(Action):
    def __init__(self, actor, targets):
        self.priority = 20
        self.actor = actor
        self.targets = targets
        self.name = "friend"

    def resolve(self, state):
        state.resolved(self)

        msg = "%s is %s" % (self.actor, state.players[self.actor].align)
        for target in state.fix(self.targets):
            state.queue.enqueue(actmessage(self.actor, target, [msg]))

        return state.queue

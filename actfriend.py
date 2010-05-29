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

        state.queue.enqueue(actmessage(self.actor, self.targets, ["%s is %s" % (self.actor, state.players[self.actor].align)] ))

        return state.queue

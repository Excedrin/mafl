from action import Action
from untrackable import Untrackable

class actmessage(Action, Untrackable):
    def __init__(self, actor, targets, args):
        self.priority = 100
        self.actor = actor
        self.targets = targets
        self.args = args
        self.name = "message"

    def resolve(self, state):
        if state.players[self.actor].living:
            for target in self.targets:
                print("message from %s to %s: %s" % (self.actor, target, self.args))

        return state.queue


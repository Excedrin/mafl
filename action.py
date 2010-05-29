class Action:
    def __init__(self, actor, targets):
        self.priority = 99999999
        self.actor = actor
        self.targets = targets
        self.name = "none"

    def __lt__(self, other):
        return self.priority < other.priority

    def __str__(self):
        return("action: %s %s %s" % (self.name, self.actor, self.targets))

    def resolve(self, state):
        return state.queue

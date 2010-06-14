class Actor:
    def __init__(self):
        self.abilities = { }
        self.acted = False

    def getability(self, name):
        if name in self.abilities:
            return self.abilities[name]
        else:
            return None

    def addability(self, ability):
        self.abilities[ability.action.name] = ability

    def removeability(self, ability):
        del abilities[ability.action.name]

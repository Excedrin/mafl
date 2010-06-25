import copy
class Actor:
    def __init__(self):
        self.abilities = {}
        self.acted = False
        self.role = ""
        self.truename = ""

    def getability(self, name):
        if name in self.abilities:
            return self.abilities[name]
        else:
            return None

    def addability(self, ability):
        self.abilities[ability.getname()] = copy.deepcopy(ability)

    def removeabilitybyname(self, name):
        del abilities[name]

    def removeability(self, ability):
        del abilities[ability.getname()]

    def setrole(self, role, faction=None):
        if faction:
            self.faction = faction
        self.role = role.name
        self.truename = getattr(role, 'truename', role.name)
        self.abilities = {}
        for x in role.abilities:
            self.addability(x)

    def addrole(self, role):
        self.role = role.name + " " + self.role
        self.truename = getattr(role, 'truename', role.name) + " " + self.truename
        for x in role.abilities:
            self.addability(x)

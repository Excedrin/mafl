from actor import Actor

class Player(Actor):
    def __init__(self, name, virtual=False):
        Actor.__init__(self)

        self.name = name
        self.faction = None
        self.living = True
        self.virtual = virtual

    def __str__(self):
        return "Player %s" %self.name

    def factionabilities(self):
        if self.faction:
            return self.faction.abilities.values()
        else:
            return []

    def allabilities(self):
        abilities = []

        abilities.extend(self.factionabilities())
        abilities.extend(self.abilities.values())

        return abilities

    def rolepm(self):
        return "abilities { %s }" % ", ".join(map(str, self.abilities.values()))

    def fullrolepm(self, state):
        farole = ""
        fa = self.factionabilities()
        if fa:
            farole = "group abilities { %s } " % ", ".join(map(str, fa))
        return "%s (%s) %s %s" %(self.role, self.faction.name, self.faction.rolepm(state), farole + self.rolepm())

    def flip(self):
        if not self.virtual:
            return "%s %s" % (self.faction.name, self.truename)
        else:
            return "%s" %(self.name)

    def unused(self, state):
        if self.living:
            for ability in self.allabilities():
                if ability.usable(self, state):
                    return True
        return False

    def done(self, state):
        if self.living:
            for ability in self.allabilities():
                if ability.usable(self, state):
                    print("setting %s used"%ability.action.name)
                    ability.used = True
                else:
                    print("%s isn't usable"%ability.action.name)

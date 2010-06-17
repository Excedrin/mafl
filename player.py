from actor import Actor

class Player(Actor):
    def __init__(self, name, faction):
        Actor.__init__(self)

        self.name = name
        self.faction = faction
        self.living = True

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
        return "%s - %s" %(self.faction.rolepm(state), farole + self.rolepm())

    def flip(self):
        return self.faction.name

    def unused(self, state):
        if self.living:
            for ability in self.allabilities():
                if ability.usable(state):
                    return True
        return False

    def done(self, state):
        if self.living:
            for ability in self.allabilities():
                if ability.usable(state):
                    print("setting %s used",ability.action.name)
                    ability.used = True
                else:
                    print("%s isn't usable",ability.action.name)

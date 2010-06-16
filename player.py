from actor import Actor

class Player(Actor):
    def __init__(self, name, faction):
        Actor.__init__(self)

        self.name = name
        self.faction = faction
        self.living = True

    def __str__(self):
        return "Player %s" %self.name

    def allabilities(self):
        abilities = []

        if self.faction:
            for _,ability in self.faction.abilities.items():
                abilities.append(ability)
        for _,ability in self.abilities.items():
            abilities.append(ability)

        return abilities

    def rolepm(self, state):
        abilitystr = ", ".join(map(str, self.allabilities()))
        return "%s - %s" %(self.faction.rolepm(state), abilitystr)

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

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
                if ability.phase is state.phase and not ability.used:
                    return True
        return False

from actor import Actor

import mafl

class Faction(Actor):
    def __init__(self, number=1):
        Actor.__init__(self)
        self.instance = number
    def __str__(self):
        return "%s%d" %(self.__class__.name, self.instance)
    def rolepm(self, state):
        return "faction baseclass"

class Sk(Faction):
    name = "sk"
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        return len(members) >= (len(alive) / 2)
    def rolepm(self, state):
        return "%s: You win if you have majority." %self.name

class Survivor(Faction):
    name = "survivor"
    def win(self, state, player):
        if player.living:
            for p in state.living():
                if p != player and p.faction.win(state, p):
                    return True
        return False
    def rolepm(self, state):
        return "%s: You win if you're alive when the game ends." %self.name

class Town(Faction):
    name = "town"
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self or isinstance(x.faction, Survivor), alive))
        return len(members) == len(alive)
    def rolepm(self, state):
        return "%s: You win when all threats to the town are eliminated." %self.name

class Mafia(Faction):
    name = "mafia"
    def __init__(self, number=1):
        Faction.__init__(self)
        self.addability(mafl.ability.Ability(mafl.actions.Kill, mafl.phase.Night))
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        return len(members) >= (len(alive) / 2)
    def rolepm(self, state):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        memberstr = ', '.join([x.name for x in members])
        return "%s: members %s, you win if you have majority." %(self.name, memberstr)

class Cult(Faction):
    name = "cult"
    def __init__(self, number=1):
        Faction.__init__(self)
        self.addability(mafl.ability.Ability(mafl.actions.Recruit, mafl.phase.Night))
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        return len(members) >= (len(alive) / 2)
    def rolepm(self, state):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        memberstr = ', '.join([x.name for x in members])
        return "%s: members %s, you win if you have majority." %(self.name, memberstr)

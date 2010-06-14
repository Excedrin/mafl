from actor import Actor

import ability
import actions 
import phase

class Faction(Actor):
    def __init__(self, number=1):
        Actor.__init__(self)
        self.instance = number
    def __str__(self):
        return "%s%d" %(self.__class__.name, self.instance)

class sk(Faction):
    name = "sk"
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        return len(members) >= (len(alive) / 2)

class survivor(Faction):
    name = "survivor"
    def win(self, state, player):
        if player.living:
            for p in state.living():
                if p != player and p.faction.win(state, p):
                    return True
        return False

class town(Faction):
    name = "town"
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self or isinstance(x.faction, survivor), alive))
        return len(members) == len(alive)

class mafia(Faction):
    name = "mafia"
    def __init__(self, number=1):
        Faction.__init__(self)
        self.addability(ability.Ability(actions.Kill, phase.Night))
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        return len(members) >= (len(alive) / 2)

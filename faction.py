from actor import Actor

class Faction(Actor):
    def __init__(self, number=1):
        Actor.__init__(self)
        self.instance = number
    def __str__(self):
        if self.instance != 1:
            return "%s%d" %(self.__class__.name, self.instance)
        else:
            return self.__class__.name
    def rolepm(self, state):
        return "faction baseclass"

class Sk(Faction):
    name = "sk"
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        return len(members) >= (len(alive) / 2)
    def rolepm(self, state):
        return "You win if you have majority."

class Survivor(Faction):
    name = "survivor"
    def win(self, state, player):
        if player.living:
            for p in state.living():
                if p != player and not isinstance(p.faction, Survivor) and p.faction.win(state, p):
                    return True
        return False
    def rolepm(self, state):
        return "You win if you're alive when the game ends."

class Town(Faction):
    name = "town"
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self or isinstance(x.faction, Survivor), alive))
        return len(members) == len(alive)
    def rolepm(self, state):
        return "You win when all threats to the town are eliminated."

class Mafia(Faction):
    name = "mafia"
    def __init__(self, number=1):
        Faction.__init__(self)
        import ability
        import actions
        import phase
        self.addability(ability.Ability(actions.Kill, phase.Night))
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        return len(members) >= (len(alive) / 2)
    def rolepm(self, state):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        memberstr = ', '.join([x.name for x in members])
        return "members ( %s ), you win if you have majority." % memberstr

class Cult(Faction):
    name = "cult"
    def __init__(self, number=1):
        Faction.__init__(self)
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        return len(members) >= (len(alive) / 2)
    def rolepm(self, state):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        memberstr = ', '.join([x.name for x in members])
        return "members ( %s ), you win if you have majority." % memberstr

def init():
    env = init.__globals__
    env['factions'] = {}
    for k,v in list(filter(lambda t:
            type(t[1]) is type
            and not t[1] is Faction
            and issubclass(t[1], Faction),
                env.items())):
        env['factions'][k] = v

init()

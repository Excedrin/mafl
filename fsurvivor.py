class Fsurvivor:
    count=0
    def __init__(self):
        Fsurvivor.count = Fsurvivor.count+1
        self.instance = Fsurvivor.count+1
        self.name = "survivor"
    def __str__(self):
        return "%s%d" %(self.name, self.instance)
    def win(self, state, player):
        if player.living:
            for p in state.living():
                if p != player and p.faction.win(state, p):
                    return True
        return False

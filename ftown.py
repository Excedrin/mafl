import fsurvivor
class Ftown:
    count=0
    def __init__(self):
        Ftown.count = Ftown.count+1
        self.instance = Ftown.count
        self.name = "town"
    def __str__(self):
        return "%s%d" %(self.name, self.instance)
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self or isinstance(x.faction, fsurvivor.Fsurvivor), alive))
        return len(members) == len(alive)

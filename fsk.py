class Fsk:
    count = 0
    def __init__(self):
        Fsk.count = Fsk.count+1
        self.instance = Fsk.count
        self.name = "sk"
    def __str__(self):
        return "%s%d" %(self.name, self.instance)
    def win(self, state, player):
        alive = state.living()
        members = list(filter(lambda x: x.faction==self, alive))
        return len(members) >= (len(alive) / 2)

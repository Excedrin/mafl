import mafl

class Setup:
    def __init__(self, rng, players):
        self.rng = rng
        self.players = list(players)

    def setroles(self):
        town = mafl.faction.Town()
        maf = mafl.faction.Mafia()
        cult = mafl.faction.Cult()
        survivor = mafl.faction.Survivor()

        self.rng.shuffle(self.players)

        if len(self.players) < 3:
            return False

        if len(self.players) == 3:
            p = self.players.pop()
            p.faction = maf
            mafl.role.Townie.setrole(p)
            for p in self.players:
                p.faction = town
                mafl.role.Townie.setrole(p)
        elif len(self.players) == 4:
            p = self.players.pop()
            p.faction = maf
            mafl.role.Townie.setrole(p)

            if self.rng.choice([True,False]): # 50/50 a doctor
                p = self.players.pop()
                p.faction = town
                mafl.role.Doctor.setrole(p)

            for p in self.players:
                p.faction = town
                mafl.role.Townie.setrole(p)
        elif len(self.players) == 5:
            p = self.players.pop()
            p.faction = maf
            mafl.role.Townie.setrole(p)

            if self.rng.choice([True,False]):
                p = self.players.pop()
                p.faction = town
                mafl.role.Doctor.setrole(p)

            for p in self.players:
                p.faction = town
                mafl.role.Townie.setrole(p)
        elif len(self.players) == 6:
            p = self.players.pop()
            p.faction = maf
            p = self.players.pop()
            p.faction = maf

            if self.rng.choice([True,False]):
                p = self.players.pop()
                p.faction = town
                mafl.role.Doctor.setrole(p)
            else:
                p = self.players.pop()
                p.faction = town
                mafl.role.Cop.setrole(p)

            for p in self.players:
                p.faction = town
                mafl.role.Townie.setrole(p)
        elif len(self.players) == 7:
            p = self.players.pop()
            p.faction = maf
            p = self.players.pop()
            p.faction = maf

            if self.rng.choice([True,False]):
                p = self.players.pop()
                p.faction = town
                mafl.role.Doctor.setrole(p)

            if self.rng.choice([True,False]):
                p = self.players.pop()
                p.faction = town
                mafl.role.Cop.setrole(p)

            for p in self.players:
                p.faction = town
                mafl.role.Townie.setrole(p)
        elif len(self.players) > 7:
            p = self.players.pop()
            p.faction = maf
            p = self.players.pop()
            p.faction = maf

            for p in self.players:
                p.faction = town
                mafl.role.Townie.setrole(p)

        return True

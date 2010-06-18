import mafl
from itertools import chain, cycle

class Setup:
    def __init__(self, rng, players):
        self.rng = rng
        self.players = list(players)

    def setroles(self):
        town = mafl.faction.Town()
        maf = mafl.faction.Mafia()
        cult = mafl.faction.Cult()
        survivor = mafl.faction.Survivor()
        sk = mafl.faction.Sk()

        self.rng.shuffle(self.players)
        n = len(self.players)
        print("setup n:",n)

        nscum = round(n * (1/4.5))
        ntown = n - nscum
        surv = []

        r = self.rng.random()
        survchance = (6/5) - (21 * (nscum / n) / 5)
        print("r",r,"survchance",survchance)
        if r <= survchance:
            surv = [survivor]
        else:
            surv = []

        factions = chain(surv, [maf for _ in range(nscum)], cycle([town]))
        for p, f in zip(self.players, factions):
            p.faction = f
            mafl.role.Townie.setrole(p)

#        if len(self.players) < 3:
#            return False
#
#        if len(self.players) == 3:
#            p = self.players.pop()
#            p.faction = maf
#            mafl.role.Townie.setrole(p)
#            for p in self.players:
#                p.faction = town
#                mafl.role.Townie.setrole(p)
#        elif len(self.players) == 4:
#            p = self.players.pop()
#            p.faction = maf
#            mafl.role.Townie.setrole(p)
#
#            if self.rng.choice([True,False]): # 50/50 a doctor
#                p = self.players.pop()
#                p.faction = town
#                mafl.role.Doctor.setrole(p)
#
#            for p in self.players:
#                p.faction = town
#                mafl.role.Townie.setrole(p)
#        elif len(self.players) == 5:
#            p = self.players.pop()
#            p.faction = maf
#            mafl.role.Townie.setrole(p)
#
#            if self.rng.choice([True,False]):
#                p = self.players.pop()
#                p.faction = town
#                mafl.role.Doctor.setrole(p)
#
#            for p in self.players:
#                p.faction = town
#                mafl.role.Townie.setrole(p)
#        elif len(self.players) == 6:
#            p = self.players.pop()
#            p.faction = maf
#            p = self.players.pop()
#            p.faction = maf
#
#            if self.rng.choice([True,False]):
#                p = self.players.pop()
#                p.faction = town
#                mafl.role.Doctor.setrole(p)
#            else:
#                p = self.players.pop()
#                p.faction = town
#                mafl.role.Cop.setrole(p)
#
#            for p in self.players:
#                p.faction = town
#                mafl.role.Townie.setrole(p)
#        elif len(self.players) == 7:
#            p = self.players.pop()
#            p.faction = maf
#            p = self.players.pop()
#            p.faction = maf
#
#            if self.rng.choice([True,False]):
#                p = self.players.pop()
#                p.faction = town
#                mafl.role.Doctor.setrole(p)
#
#            if self.rng.choice([True,False]):
#                p = self.players.pop()
#                p.faction = town
#                mafl.role.Cop.setrole(p)
#
#            for p in self.players:
#                p.faction = town
#                mafl.role.Townie.setrole(p)
#        elif len(self.players) > 7:
#            p = self.players.pop()
#            p.faction = maf
#            p = self.players.pop()
#            p.faction = maf
#
#            for p in self.players:
#                p.faction = town
#                mafl.role.Townie.setrole(p)

        return True

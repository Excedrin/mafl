import random
import mafl
class Setup:
    def __init__(self, players):
        self.players = list(players)

    def setroles(self):
        town = mafl.faction.Town()
        maf = mafl.faction.Mafia()
        survivor = mafl.faction.Survivor()

        random.shuffle(self.players)

        if len(self.players) < 3:
            return False

        if len(self.players) == 3:
            p = self.players.pop()
            p.faction = maf
            mafl.role.Townie().setrole(p)
            for p in self.players:
                p.faction = town
                mafl.role.Townie().setrole(p)
        elif len(self.players) == 4:
            p = self.players.pop()
            p.faction = maf
            mafl.role.Townie().setrole(p)

            if random.choice([True,False]): # 50/50 a doctor
                p = self.players.pop()
                p.faction = town
                mafl.role.Doctor().setrole(p)

            for p in self.players:
                p.faction = town
                mafl.role.Townie().setrole(p)
        elif len(self.players) == 5:
            p = self.players.pop()
            p.faction = maf
            mafl.role.Townie().setrole(p)

            if random.choice([True,False]):
                p = self.players.pop()
                p.faction = town
                mafl.role.Doctor().setrole(p)

            for p in self.players:
                p.faction = town
                mafl.role.Townie().setrole(p)
        elif len(self.players) == 6:
            p = self.players.pop()
            p.faction = maf
            p = self.players.pop()
            p.faction = maf

            if random.choice([True,False]):
                p = self.players.pop()
                p.faction = town
                mafl.role.Doctor().setrole(p)
            else:
                p = self.players.pop()
                p.faction = town
                mafl.role.Cop().setrole(p)

            for p in self.players:
                p.faction = town
                mafl.role.Townie().setrole(p)
        elif len(self.players) == 7:
            p = self.players.pop()
            p.faction = maf
            p = self.players.pop()
            p.faction = maf

            if random.choice([True,False]):
                p = self.players.pop()
                p.faction = town
                mafl.role.Doctor().setrole(p)

            if random.choice([True,False]):
                p = self.players.pop()
                p.faction = town
                mafl.role.Cop().setrole(p)

            for p in self.players:
                p.faction = town
                mafl.role.Townie().setrole(p)
        elif len(self.players) > 7:
            p = self.players.pop()
            p.faction = maf
            p = self.players.pop()
            p.faction = maf

            for p in self.players:
                p.faction = town
                mafl.role.Townie().setrole(p)

        return True

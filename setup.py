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

        self.rng.shuffle(self.players)
        n = len(self.players)
        if n < 3:
            return False

        print("setup n:",n)

        nscum = round(n * (1/4.5))
        neutrals = []

        r = self.rng.random()
        survchance = (6/5) - (21 * (nscum / n) / 5)
        print("r",r,"survchance",survchance)
        if r <= survchance:
            neutrals.append(survivor)

        r = self.rng.random()
        skchance = survchance / 1.6
        print("r",r,"skchance",skchance)
        if r <= skchance:
            sk = mafl.faction.Sk()
            neutrals.append(sk)

        baddies = maf
        if n > 7:
            if self.rng.random() > 0.9:
                baddies = cult
                if n > 9:
                    nscum = 2
                else:
                    nscum = 1

        scum = neutrals + [baddies for _ in range(nscum)]
        ntown = n - (nscum + len(neutrals))
        print("ntown", ntown)

        scumroles = []
        for p, f in zip(self.players, scum):
            p.faction = f
            fc = f.__class__
#            r = self.rng.choice(list(filter(lambda x: x.basic, mafl.role.faction[fc])))
            r = self.rng.choice(mafl.role.faction[fc])
            scumroles.append(r)
            p.setrole(r)
            print("calling setrole for",p.name)

        scumpower = sum([x.power for x in scumroles])
        print("scumpower",scumpower,[mafl.role.getname(x) for x in scumroles])

        townroles = []
        townpower = 0
        for x in range(ntown):
            if townpower > scumpower + 0.5:
                r = self.rng.choice(list(filter(lambda x: x.power <= 0, mafl.role.faction[mafl.faction.Town])))
                print("too much town power, picking bad role",mafl.role.getname(r))
            elif townpower > len(townroles) * 0.2 or townpower > scumpower:
                r = self.rng.choice(list(filter(lambda x: x.basic, mafl.role.faction[mafl.faction.Town])))
                print("too much town power, picking basic role",mafl.role.getname(r))
            else:
                r = self.rng.choice(mafl.role.faction[mafl.faction.Town])
            townroles.append(r)
            townpower = sum([x.power for x in townroles])

            p = self.players.pop()
            p.faction = town
            p.setrole(r)
            print("calling setrole for",p.name)

        print("townpower",townpower,[mafl.role.getname(x) for x in townroles])

        return True

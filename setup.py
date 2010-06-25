import mafl
from itertools import chain, cycle

def bastard(role, n, fac):
    return role.power(n, fac) < 0 or getattr(role, 'truename', False)

class Setup:
    def __init__(self, rng, players):
        self.rng = rng
        self.players = list(players)

    def setroles(self):
        bastardly = 0.15
        cultchance = 0.10

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
        survchance = (6/5) - (21 * (nscum / (n-nscum)) / 5)
        print("r",r,"survchance",survchance)
        if r <= survchance:
            neutrals.append(survivor)

        r = self.rng.random()
        skchance = survchance / 2
        print("r",r,"skchance",skchance)
        skcount = 0
        if r <= skchance:
            skcount += 1
            sk = mafl.faction.Sk(skcount)
            neutrals.append(sk)

        baddies = maf
        if n > 7:
            if self.rng.random() < cultchance:
                baddies = cult
                if n > 9:
                    nscum = 2
                else:
                    nscum = 1
            else:
                if nscum == 1 and self.rng.random() > 0.5:
                    skcount += 1
                    baddies = mafl.faction.Sk(skcount)

        scum = neutrals + [baddies for _ in range(nscum)]
        ntown = n - (nscum + len(neutrals))
        print("ntown", ntown)

        if n <= 4:
            maxscumpower = 0.5
        else:
            maxscumpower = 99

        scumroles = []
        for p, f in zip(self.players, scum):
            p.faction = f
            fc = f.__class__
            okroles = list(filter(lambda x: x.power(n, fc) <= maxscumpower, mafl.role.faction[fc]))
            r = self.rng.choice(okroles)
            scumroles.append(r)
            p.setrole(r)
            print("calling setrole for",p.name)

        scumpower = sum([x.power(n, align) * (0.5 if align.__class__ is mafl.faction.Survivor else 1) for (x,align) in zip(scumroles, scum)])
        print("scumpower",scumpower,[mafl.role.getname(x) for x in scumroles])

        avgscumpower = scumpower / len(scumroles)

        if baddies == cult:
            scumpower += 1
        maxpower = scumpower
        townroles = []
        townpower = 0

        fac = mafl.faction.Town
        badroles = list(filter(lambda x: bastard(x, n, fac), mafl.role.faction[fac]))
        basicroles = list(filter(lambda x: x.basic, mafl.role.faction[fac]))
        normalroles = list(filter(lambda x: not bastard(x, n, fac)
            and x.power(n, fac) > 0
            and x.power(n, fac) < maxpower, mafl.role.faction[fac]))

        print("scumpower %0.2f" % scumpower)
        for x in range(ntown):
            print("townpower %0.2f"%(townpower))
            if townpower > scumpower:
                if self.rng.random() > bastardly:
                    r = self.rng.choice(basicroles)
                    print("too much town power, picking basic role",mafl.role.getname(r))
                else:
                    r = self.rng.choice(badroles)
                    print("repick",mafl.role.getname(r))
                    if r in townroles:
                        r = self.rng.choice(badroles)
                    print("too much town power, picking bad role",mafl.role.getname(r))
            else:
                if normalroles:
                    r = self.rng.choice(normalroles)
                    print("repick",mafl.role.getname(r))
                    if r in townroles:
                        r = self.rng.choice(normalroles)
                    print("picking normal role",mafl.role.getname(r))
                else:
                    r = self.rng.choice(basicroles)
                    print("no normal roles, picking basic role",mafl.role.getname(r))
            townroles.append(r)
            townpower = sum([x.power(n, mafl.faction.Town) for x in townroles])

            p = self.players.pop()
            p.faction = town
            p.setrole(r)
            print("calling setrole for",p.name)

        print("townpower",townpower,[mafl.role.getname(x) for x in townroles])

        return True

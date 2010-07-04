import mafl
from itertools import chain, cycle

def bastard(role, n, fac):
    return role.power(n, fac) < 0 or getattr(role, 'truename', False)

class Setup:
    def __init__(self, rng):
        self.rng = rng
        self.roles = []

    def setroles(self, players):
        self.rng.shuffle(players)
        for p, (r,f) in zip(players, self.roles):
            p.setrole(r,f)

    def getroles(self, n):
        bastardly = 0.15
        cultchance = 0.10

        town = mafl.faction.Town()
        maf = mafl.faction.Mafia()
        cult = mafl.faction.Cult()
        survivor = mafl.faction.Survivor()

        if n < 3:
            return False

        print("setup n:",n)

        nscum = int(round(n * (1/4.5)))
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

        scum = [baddies for _ in range(nscum)]
        ntown = n - (nscum + len(neutrals))
        print("ntown", ntown)

        if n <= 4:
            maxscumpower = 0.5
        else:
            maxscumpower = 99

        neutralroles = []
        for f in neutrals:
            fc = f.__class__
            okroles = list(filter(lambda x: x.power(n, fc) <= maxscumpower, mafl.role.faction[fc]))
            r = self.rng.choice(okroles)
            neutralroles.append((r, f))

        scumroles = []

        if baddies == cult:
            scumroles.append((mafl.role.CultLeader, cult))
            onecl = scum.pop()
            if onecl != cult:
                raise ValueError

        for f in scum:
            fc = f.__class__
            okroles = list(filter(lambda x: x.power(n, fc) <= maxscumpower, mafl.role.faction[fc]))
            r = self.rng.choice(okroles)
            scumroles.append((r, f))

        neutralpower = sum([x.power(n, align) for (x,align) in neutralroles])
        scumpower = sum([x.power(n, align) for (x,align) in scumroles]) + (neutralpower / 2)
        print("scumpower",scumpower,[x.getname() for x,_ in scumroles])

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
                    print("too much town power, picking basic role",r.getname())
                else:
                    r = self.rng.choice(badroles)
                    if (r,town) in townroles:
                        print("repick",r.getname())
                        r = self.rng.choice(badroles)
                    print("too much town power, picking bad role",r.getname())
            else:
                if normalroles:
                    r = self.rng.choice(normalroles)
                    if (r,town) in townroles:
                        print("repick",r.getname())
                        r = self.rng.choice(normalroles)
                    print("picking normal role",r.getname())
                else:
                    r = self.rng.choice(basicroles)
                    print("no normal roles, picking basic role",r.getname())
            townroles.append((r, town))
            townpower = sum([x.power(n, mafl.faction.Town) for x,_ in townroles])

        print("townpower",townpower,[x.getname() for x,_ in townroles])

        self.roles = townroles + scumroles + neutralroles
        return True

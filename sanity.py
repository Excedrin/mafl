import mafl
import random

class Sanity:
    def __init__(self, factions=[mafl.faction.Town, mafl.faction.Mafia]):
        self.factions = factions
    def result(self, p):
        notfaction = []
        for f in self.factions:
            if isinstance(p.faction, f):
                return "is " + f.name
            else:
                notfaction.append(f.name)
        return "isn't " + " or ".join(notfaction)

class Sane(Sanity):
    pass

# insane inspect can still tell when a faction isn't any of the factions
# it knows about
class Insane(Sanity):
    def result(self, p):
        isfaction = []
        notfaction = []
        for f in self.factions:
            if isinstance(p.faction, f):
                isfaction.append(f.name)
            else:
                notfaction.append(f.name)
        if isfaction:
            return "is " + notfaction.pop()
        else:
            return "isn't " + " or ".join(notfaction)

class Paranoid(Sanity):
    def __init__(self, factions=[mafl.faction.Mafia]):
        self.factions = factions
    def result(self, p):
        f = random.choice(self.factions)
        return "is " + f.name

class Naive(Paranoid):
    def __init__(self, factions=[mafl.faction.Town]):
        self.factions = factions
    def result(self, p):
        return Paranoid.result(self, p)

class Stoned(Sanity):
    def result(self, p):
        return "isn't " + " or ".join([f.name for f in self.factions])

class Random(Stoned, Naive):
    def result(self, p):
        if random.choice((True,False)):
            return Stoned.result(self, p)
        else:
            return Paranoid.result(self, p)

class Rolecop(Sanity):
    def result(self, p):
        return p.rolepm()

if __name__ == "__main__":
    maf = mafl.Player("maf", mafl.faction.Mafia())
    town = mafl.Player("town", mafl.faction.Town())
    sk = mafl.Player("sk", mafl.faction.Sk())

    cs = Sane()
    ci = Insane()
    cp = Paranoid()
    cn = Naive()
    cz = Stoned()
    cr = Random()

    print("cst",cs.result(town))
    print("csm",cs.result(maf))
    print("css",cs.result(sk))

    print("cit",ci.result(town))
    print("cim",ci.result(maf))
    print("cis",ci.result(sk))

    print("czt",cz.result(town))
    print("czm",cz.result(maf))
    print("czs",cz.result(sk))

    print("cnt",cn.result(town))
    print("cnm",cn.result(maf))
    print("cns",cn.result(sk))

    print("cpt",cp.result(town))
    print("cpm",cp.result(maf))
    print("cps",cp.result(sk))

    print("crt",cr.result(town))
    print("crm",cr.result(maf))
    print("crs",cr.result(sk))

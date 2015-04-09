import mafl
from itertools import chain, cycle

def bastard(role, n, fac):
    return role.power(n, fac) < 0 or getattr(role, 'truename', False)

class Setup:
    def __init__(self, rng, args):
        self.rng = rng
        self.roles = []
        self.args = args

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

class SS3(Setup):
    def getroles(self, n):
        town = mafl.faction.Town()
        maf = mafl.faction.Mafia()
        self.roles = [(mafl.role.SuperSaint, town),
                      (mafl.role.Townie, town),
                      (mafl.role.Mafioso, maf)]
        if n == 3:
            return True
        elif n > 3:
            moremaf = int(n / 7)
            self.roles.extend([(mafl.role.Mafioso, maf) for x in range(moremaf)])
            r = lambda: self.rng.choice((mafl.role.SuperSaint, mafl.role.Townie))
            self.roles.extend([(r(), town) for x in range(n - 3 - moremaf)])
            return True
        else:
            return False

class C9(Setup):
    def getroles(self, n):
        if n == 7:
            town = mafl.faction.Town()
            maf = mafl.faction.Mafia()
            self.roles.append((mafl.role.Mafioso, maf))
            self.roles.append((mafl.role.Mafioso, maf))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            r1 = self.rng.choice((mafl.role.Cop, mafl.role.Townie))
            r2 = self.rng.choice((mafl.role.Doctor, mafl.role.Townie))
            self.roles.append((r1, town))
            self.roles.append((r2, town))
            return True
        else:
            return False

class F11(Setup):
    def getroles(self, n):
        if n == 9:
            town = mafl.faction.Town()
            maf = mafl.faction.Mafia()
            setupno = self.rng.randint(0,3)

            if setupno == 0:
                self.roles.append((mafl.role.Roleblocker, maf))
                self.roles.append((mafl.role.Townie, town))
                self.roles.append((mafl.role.Townie, town))
            elif setupno == 1:
                self.roles.append((mafl.role.Mafioso, maf))
                self.roles.append((mafl.role.Townie, town))
                self.roles.append((mafl.role.Cop, town))
            elif setupno == 2:
                self.roles.append((mafl.role.Mafioso, maf))
                self.roles.append((mafl.role.Townie, town))
                self.roles.append((mafl.role.Doctor, town))
            elif setupno == 3:
                self.roles.append((mafl.role.Roleblocker, maf))
                self.roles.append((mafl.role.Cop, town))
                self.roles.append((mafl.role.Doctor, town))

            self.roles.append((mafl.role.Mafioso, maf))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            return True
        else:
            return False

class Matrix6(Setup):
    def getroles(self, n):
        if n == 9:
            town = mafl.faction.Town()
            maf = mafl.faction.Mafia()
            setupno = self.rng.randint(0,5)

            if setupno == 0:
                self.roles.append((mafl.role.Mafioso, maf))
                self.roles.append((mafl.role.Townie, town))
                self.roles.append((mafl.role.Jailer, town))
            elif setupno == 1:
                self.roles.append((mafl.role.Roleblocker, maf))
                self.roles.append((mafl.role.Cop, town))
                self.roles.append((mafl.role.Doctor, town))
            elif setupno == 2:
                self.roles.append((mafl.role.Mafioso, maf))
                self.roles.append((mafl.role.OneShotBulletproof, town))
                self.roles.append((mafl.role.Tracker, town))
            elif setupno == 3:
                self.roles.append((mafl.role.Jailer, town))
                self.roles.append((mafl.role.Roleblocker, maf))
                self.roles.append((mafl.role.OneShotBulletproof, town))
            elif setupno == 4:
                self.roles.append((mafl.role.Cop, town))
                self.roles.append((mafl.role.Townie, town))
                self.roles.append((mafl.role.Mafioso, maf))
            elif setupno == 5:
                self.roles.append((mafl.role.Tracker, town))
                self.roles.append((mafl.role.Mafioso, maf))
                self.roles.append((mafl.role.Doctor, town))

            self.roles.append((mafl.role.Mafioso, maf))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            self.roles.append((mafl.role.Townie, town))
            return True
        else:
            return False

class Straight(Setup):
# straight: Only Townies, sane Cops, Doctors, Vigilantes, Roleblockers, 
# Mafiosos, and Godfathers appear.
    def getroles(self, n):
        town = mafl.faction.Town()
        maf = mafl.faction.Mafia()

        if n < 3:
            return False

        print("setup n:",n)

        nscum = int(round(n * (1/4.5)))
        scum = [maf for _ in range(nscum)]
        ntown = n - nscum
        print("ntown", ntown)

        if n <= 4:
            maxscumpower = 0.5
        else:
            maxscumpower = 99

        scumroles = []

        okroles = [mafl.role.Roleblocker, mafl.role.Mafioso, mafl.role.Godfather]
        for f in scum:
            fc = f.__class__
            r = self.rng.choice(okroles)
            if (r,maf) in scumroles:
                print("repick",r.getname())
                r = self.rng.choice(okroles)
            scumroles.append((r, f))

        scumpower = sum([x.power(n, align) for (x,align) in scumroles])
        print("scumpower",scumpower,[x.getname() for x,_ in scumroles])

        avgscumpower = scumpower / len(scumroles)

        maxpower = scumpower
        townroles = []
        townpower = 0

        fac = mafl.faction.Town
        normalroles = [mafl.role.Townie, mafl.role.Cop, mafl.role.Doctor, 
                       mafl.role.Vigilante, mafl.role.Roleblocker]

        print("scumpower %0.2f" % scumpower)
        for x in range(ntown):
            print("townpower %0.2f"%(townpower))
            if townpower > scumpower:
                r = mafl.role.Townie
                print("too much town power, picking basic role",r.getname())
            else:
                r = self.rng.choice(normalroles)
                if (r,town) in townroles:
                    print("repick",r.getname())
                    r = self.rng.choice(normalroles)
                print("picking normal role",r.getname())
            townroles.append((r, town))
            townpower = sum([x.power(n, mafl.faction.Town) for x,_ in townroles])

        print("townpower",townpower,[x.getname() for x,_ in townroles])

        self.roles = townroles + scumroles
        return True

class Fixed(Setup):
    def getroles(self, n):
        factions = {}

        for arg in self.args:
            (rolename, facname) = arg.split(",")
            print("rolename",rolename,"facname",facname)
            if not facname in factions:
                facclass = mafl.faction.factions.get(facname, None)
                if facclass:
                    factions[facname] = facclass()
                else:
                    return False
            faction = factions[facname]
            role = mafl.role.roles.get(rolename, None)
            if faction and role:
                self.roles.append((role, faction))
            else:
                return False

        return True

def init():
    env = init.__globals__

    env['setups'] = {}

    for k,v in list(filter(lambda t:
            (type(t[1]) is type
            and issubclass(t[1], Setup)),
                env.items())):
        env['setups'][k] = v

init()

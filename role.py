from ability import Ability
from actions import *
from phase import *
from sanity import *
from faction import *
from misc import *

import random

class RoleBase:
    basic = False
    name = "baserole"
    factions = [Town, Cult, Mafia, Sk, Survivor]
    abilities = []
    def power(n, align):
        return 0
    @classmethod
    def getname(cls):
        return getattr(cls, 'truename', cls.name)

class Townie(RoleBase):
    basic = True
    factions = [Town]
    name = "Townie"
    abilities = [Ability(Vote, Day, free=True, public=True, optargs=True,
                    nosteal=True, restrict=[Ability.LivingOrNL]),
                Ability(Vote, Day, name='unvote', free=True, public=True, optargs=True,
                    nosteal=True, restrict=[Ability.LivingOrNL])]
    def power(n, align):
        return 0

class Mafioso(RoleBase):
    basic = True
    factions = [Mafia]
    name = "Mafioso"
    abilities = Townie.abilities
    def power(n, align):
        return 0.33

class Cultist(RoleBase):
    basic = True
    factions = [Cult]
    name = "Cultist"
    abilities = Townie.abilities
    def power(n, align):
        return 0

class CultLeader(RoleBase):
    basic = True
    factions = [] # handled specially in setup generator
    name = "Cult Leader"
    abilities = Townie.abilities + \
        [Ability(Recruit, args={'role':Cultist}),
         Ability(Reflex, Any, auto=True, nosteal=True, resolvers=[Ability.Self()],
            args={'action':Suicide(0, [], args={'how':'drank the Kool-Aid','nobus':True}),
                  'resolvers':[Ability.AllTeam()],
                  'triggers':[Lynch, Kill, SuperKill, PoisonKill]} )]
    def power(n, align):
        return 0.7

class Psychiatrist(RoleBase):
    factions = [Town]
    name = "Psychiatrist"
    abilities = Townie.abilities + \
        [Ability(Recruit, name='psych', args={'role':Townie,'okalign':[Sk],
            'msg':'treated'})]
    def power(n, align):
        return 0.3

class SurvivorBase(RoleBase):
    basic = True
    factions = [Survivor]
    name = "Survivor"
    abilities = Townie.abilities
    def power(n, align):
        return 0

class SerialKiller(RoleBase):
    basic = True
    factions = [Sk]
    name = "Serial Killer"
    abilities = Townie.abilities + [Ability(Kill)]
    def power(n, align):
        return 0.7

class Vigilante(RoleBase):
    factions = [Town]
    name = "Vigilante"
    abilities = Townie.abilities + [Ability(Kill)]
    def power(n, align):
        return 0.7

class CrazedFiend(RoleBase):
    factions = [Town, Sk]
    name = "Crazed Fiend"
    abilities = Townie.abilities + [Ability(Kill, Any, uses=Some(1))]
    def power(n, align):
        if align is Sk:
            return max((4/3) - (n/9), 0.3)
        return 0.7

class GraveVigilante(RoleBase):
    factions = [Town, Survivor]
    name = "Grave Vigilante"
    abilities = Townie.abilities + [Ability(Kill, Any, uses=Some(1), ghost=True)]
    def power(n, align):
        return 0.7

class Cop(RoleBase):
    factions = [Town]
    abilities = Townie.abilities + [Ability(Inspect)]
    name = "Cop"
    def power(n, align):
        return 0.4

class RoleCop(RoleBase):
    factions = [Town, Mafia]
    abilities = Townie.abilities + [Ability(Inspect, args={'sanity':Rolecop()})]
    name = "Role Cop"
    def power(n, align):
        return 0.5

class DevilsAdvocate(RoleBase):
    factions = [Sk]
    name = "Devil's Advocate"
    abilities = Townie.abilities + [Ability(Inspect, args={'sanity':Rolecop()}), Ability(Kill, Day)]
    def power(n, align):
        return 0.72

class Doctor(RoleBase):
    factions = [Town, Mafia]
    name = "Doctor"
    abilities = Townie.abilities + [Ability(Protect)]
    def power(n, align):
        return 0.4

class BusDriver(RoleBase):
    factions = [Town, Mafia]
    name = "Bus Driver"
    abilities = Townie.abilities + [Ability(Bus, resolvers=[Ability.User(), Ability.User()])]
    def power(n, align):
        return 0.5

class Roleblocker(RoleBase):
    factions = [Town, Survivor, Mafia]
    name = "Roleblocker"
    abilities = Townie.abilities + [Ability(Block),
         Ability(Immune, Any, auto=True, resolvers=[Ability.Self()],
                    args={'immune':[Block]})]
    def power(n, align):
        return 0.3

class Jailer(RoleBase):
    factions = [Town, Survivor, Mafia]
    name = "Jailer"
    abilities = Townie.abilities + [Ability(Jail)]
    def power(n, align):
        return 0.33

class Alien(RoleBase):
    factions = [Town, Survivor, Mafia]
    name = "Alien"
    abilities = Townie.abilities + [Ability(Abduct)]
    def power(n, align):
        return 0.43

class Redirecter(RoleBase):
    factions = [Town, Mafia]
    name = "Redirecter"
    abilities = Townie.abilities + [Ability(Redirect, resolvers=[Ability.User(), Ability.User()])]
    def power(n, align):
        return 0.5

class Magnet(RoleBase):
    factions = [Town, Survivor]
    name = "Magnet"
    abilities = Townie.abilities + [Ability(Redirect, name="attract", resolvers=[Ability.User(), Ability.Self()])]
    def power(n, align):
        return 0.2

class Randomizer(RoleBase):
    factions = [Town, Survivor, Mafia]
    name = "Randomizer"
    abilities = Townie.abilities + [Ability(Redirect, name="randomize", resolvers=[Ability.User(), Ability.Random()])]
    def power(n, align):
        return 0.3

class Tracker(RoleBase):
    factions = [Town, Mafia]
    name = "Tracker"
    abilities = Townie.abilities + [Ability(Track)]
    def power(n, align):
        return 0.4

class Watcher(RoleBase):
    factions = [Town, Survivor, Mafia]
    name = "Watcher"
    abilities = Townie.abilities + [Ability(Watch)]
    def power(n, align):
        return 0.35

class NightWatchman(RoleBase):
    factions = [Town, Mafia]
    name = "Night Watchman"
    abilities = Townie.abilities + [Ability(Patrol)]
    def power(n, align):
        if align is Mafia:
            return 0.5
        return 0.45

class DoubleVoter(RoleBase):
    factions = [Town]
    name = "Double Voter"
    abilities = Townie.abilities + [Ability(Vote, Day, free=True, public=True, optargs=True, args={'maxvotes':2} )]
    def power(n, align):
        return max(1.8 - 0.1 * n, 0.3)

class NonVoter(RoleBase):
    factions = [Town]
    name = "Nonvoter"
    abilities = Townie.abilities + [Ability(Vote, Day, free=True, public=True, optargs=True, args={'maxvotes':0} )]
    def power(n, align):
        return min(0.1 * n - 1.3, 0)

class ParanoidGunOwner(RoleBase):
    factions = [Town, Survivor]
    name = "Paranoid Gun Owner"
    abilities = Townie.abilities + [Ability(Reflex, Any, auto=True, resolvers=[Ability.Self()], args={'action':Kill(0, [], args={'nobus':True})} )]
    def power(n, align):
        return 0.75

class Eavesdropper(RoleBase):
    factions = [Town, Cult, Survivor, Mafia]
    name = "Eavesdropper"
    abilities = Townie.abilities + [Ability(Eavesdrop)]
    def power(n, align):
        if align is Cult:
            return 0.6
        return 0.4

class Coward(RoleBase):
    factions = [Town, Survivor, Mafia]
    name = "Coward"
    abilities = Townie.abilities + [Ability(Hide, uses=Some(1), resolvers=[Ability.Self()] )]
    def power(n, align):
        if align is Survivor:
            return 0.2
        return 0.18

class Framer(RoleBase):
    factions = [Mafia]
    name = "Framer"
    abilities = Townie.abilities + [Ability(Alter, name="frame", restrict=[Ability.NonTeam, Ability.Living, Ability.NonSelf])]
    def power(n, align):
        return 0.35

class Lawyer(RoleBase):
    factions = [Mafia]
    name = "Lawyer"
    abilities = Townie.abilities + [Ability(Alter, name="clear", restrict=[Ability.SameTeam, Ability.Living, Ability.NonSelf])]
    def power(n, align):
        if n <= 6:
            return 0.1
        return 0.35

class Agent(RoleBase):
    factions = [Mafia]
    name = "Agent"
    abilities = Townie.abilities + [Ability(Alter)]
    def power(n, align):
        return 0.4

class Miller(RoleBase):
    factions = [Town]
    name = "Townie"
    truename = "Miller"
    abilities = Townie.abilities + [Ability(Alter, Any, auto=True, resolvers=[Ability.Self()] )]
    def power(n, align):
        return -0.1

class DeathMiller(RoleBase):
    factions = [Town]
    name = "Townie"
    truename = "Death Miller"
    abilities = Townie.abilities + \
        [Ability(Alter, Any, auto=True, resolvers=[Ability.Self()] ),
         Ability(FakeFlip, Any, auto=True, resolvers=[Ability.Self()], args={'role':'Mafioso', 'faction':Mafia} )]
    def power(n, align):
        return -0.1

class Godfather(RoleBase):
    factions = [Mafia]
    name = "Godfather"
    abilities = Townie.abilities + \
        [Ability(Alter, Any, auto=True, resolvers=[Ability.Self()]), 
         Ability(Immune, Any, auto=True, resolvers=[Ability.Self()],
                    args={'immune':[Kill]})]
    def power(n, align):
        return 0.6

class Lynchproof(RoleBase):
    factions = [Town, Survivor]
    name = "Lynchproof"
    abilities = Townie.abilities + \
        [Ability(Immune, Any, auto=True, resolvers=[Ability.Self()],
                    args={'immune':[Lynch]})]
    def power(n, align):
        return 0.3

class Ascetic(RoleBase):
    factions = [Town, Survivor, Mafia, Cult]
    name = "Ascetic"
    abilities = Townie.abilities + \
        [Ability(Immune, Any, auto=True, resolvers=[Ability.Self()],
                    args={'not':0,'immune':[Kill, Lynch]})]
    def power(n, align):
        if align is Cult:
            return 0.4
        if align is Mafia:
            return 0.3
        return 0.2

class Bulletproof(RoleBase):
    factions = [Town, Mafia]
    name = "Bulletproof"
    abilities = Townie.abilities + \
        [Ability(Immune, Any, auto=True, resolvers=[Ability.Self()],
                    args={'immune':[Kill]})]
    def power(n, align):
        return 0.3

class Commando(RoleBase):
    factions = [Town, Sk]
    name = "Commando"
    abilities = Bulletproof.abilities + Vigilante.abilities
    def power(n, align):
        if align is Sk:
            return 1.1
        return 1

class ChainsawMurderer(RoleBase):
    factions = [Sk]
    name = "Chainsaw Murderer"
    abilities = Townie.abilities + [Ability(SuperKill)]
    def power(n, align):
        return 0.71

class Ninja(RoleBase):
    factions = [Town, Sk]
    name = "Ninja"
    abilities = Townie.abilities + [Ability(Kill, args={'untrackable':True})]
    def power(n, align):
        if align is Sk:
            return 0.7
        return 0.61

class Delayer(RoleBase):
    factions = [Town, Survivor, Mafia, Cult]
    name = "Delayer"
    abilities = Townie.abilities + [Ability(Delay, args={'phases':2})]
    def power(n, align):
        return 0.5

class Poisoner(RoleBase):
    factions = [Town, Survivor, Sk]
    name = "Poisoner"
    abilities = Townie.abilities + [Ability(Poison, Day)]
    def power(n, align):
        if align is Survivor:
            return 1
        if align is Town:
            return max(1.16666 - 0.055555 * n, 0.3)
        return 0.5

class PoisonDoctor(RoleBase):
    factions = [Town, Survivor, Mafia]
    name = "Poison Doctor"
    abilities = Townie.abilities + [Ability(Antidote, restrict=[Ability.Living])]
    def power(n, align):
        return 0.2

class HumanShield(RoleBase):
    factions = [Town, Survivor, Mafia]
    name = "Human Shield"
    abilities = Townie.abilities + [Ability(Guard, args={'guard':Guard.Self})]
    def power(n, align):
        return 0.2

class Bodyguard(RoleBase):
    factions = [Town]
    name = "Bodyguard"
    abilities = Townie.abilities + [Ability(Guard)]
    def power(n, align):
        return 0.4

class EliteBodyguard(RoleBase):
    factions = [Town]
    name = "Elite Bodyguard"
    abilities = Townie.abilities + [Ability(Guard, args={'guard':Guard.Other})]
    def power(n, align):
        return max(0.98 - 0.06 * n, 0.2)

class Friend(RoleBase):
    factions = [Town, Survivor]
    name = "Friendly Neighbor"
    abilities = Townie.abilities + [Ability(Friend, Day)]
    def power(n, align):
        return max(0.6 - 0.033333 * n, 0.2)

class Joat(RoleBase):
    factions = [Town]
    name = "Jack of all Trades"
    abilities = Townie.abilities + [Ability(Kill, uses=Some(1)),
                Ability(Inspect, uses=Some(1)), Ability(Protect, uses=Some(1)),
                Ability(Block, uses=Some(1))]
    def power(n, align):
        return max(0.8 - 0.033333 * n, 0.2)

class Stalker(RoleBase):
    factions = [Town]
    name = "Stalker"
    abilities = Townie.abilities + [Ability(Kill), Ability(Inspect)]
    def power(n, align):
        return 1

class Skulker(RoleBase):
    factions = [Town, Survivor]
    name = "Skulker"
    abilities = Townie.abilities + [Ability(Reflex, Any, auto=True, resolvers=[Ability.Self()], args={'action':Suicide(0, [], args={'nobus':True})} )]
    def power(n, align):
        return -0.2

class SuperSaint(RoleBase):
    factions = [Town, Survivor]
    name = "Super-Saint"
    abilities = Townie.abilities + \
        [Ability(Reflex, Any, auto=True, resolvers=[Ability.Self()],
            args={'action':Kill(0, [], args={'how':'was killed by an angry mob','nobus':True}),
                  'triggers':[Lynch]} )]
    def power(n, align):
        return 0.3

class Bomb(RoleBase):
    factions = [Town, Survivor]
    name = "Bomb"
    abilities = Townie.abilities + \
        [Ability(Reflex, Any, auto=True, resolvers=[Ability.Self()],
            args={'action':Kill(0, [], args={'how':'was killed by an explosion','nobus':True}),
                  'triggers':[Lynch, Kill, SuperKill]} )]
    def power(n, align):
        return 0.6

class Reviver(RoleBase):
    factions = [Town, Survivor]
    name = "Reviver"
    abilities = Townie.abilities + \
        [Ability(Resurrect, Any, auto=True, resolvers=[Ability.Self()], uses=Some(1))]
    def power(n, align):
        return 0.25

class Copycat(RoleBase):
    factions = [Town, Survivor]
    name = "Copycat"
    abilities = Townie.abilities + \
        [Ability(Copy)]
    def power(n, align):
        return 0.6

class Disabler(RoleBase):
    factions = [Town, Mafia]
    name = "Disabler"
    abilities = Townie.abilities + \
        [Ability(Disable)]
    def power(n, align):
        return 0.35

class Thief(RoleBase):
    factions = [Town, Mafia]
    name = "Thief"
    abilities = Townie.abilities + \
        [Ability(Steal)]
    def power(n, align):
        return 0.4

class Shuffler(RoleBase):
    factions = [Town, Mafia]
    name = "Shuffler"
    abilities = Townie.abilities + \
        [Ability(Swap, name="shuffle", resolvers=[Ability.RandomNonSelfUnique(), Ability.RandomNonSelfUnique()])]
    def power(n, align):
        return 0.4

class Changeling(RoleBase):
    factions = [Town, Survivor]
    name = "Changeling"
    abilities = Townie.abilities + \
        [Ability(Swap, name="exchange", resolvers=[Ability.User(), Ability.Self()])]
    def power(n, align):
        return 0.35

class Mimic(RoleBase):
    factions = [Town, Mafia]
    name = "Mimic"
    abilities = Townie.abilities + \
        [Ability(Bus, name="mimic", resolvers=[Ability.User(), Ability.Self()])]
    def power(n, align):
        return 0.23

class Morpher(RoleBase):
    factions = [Town, Sk]
    name = "Morpher"
    abilities = Townie.abilities + \
        [Ability(Morph)]
    def power(n, align):
        return 0.33

class AntiDoctor(RoleBase):
    factions = [Mafia]
    name = "Anti-Doctor"
    abilities = Townie.abilities + \
        [Ability(ReverseProtect)]
    def power(n, align):
        return 0.4

class Voteblocker(RoleBase):
    factions = [Town, Mafia]
    name = "Voteblocker"
    abilities = Townie.abilities + \
        [Ability(Voteop)]
    def power(n, align):
        if align is Mafia:
            return max((4/3) - (n/9), 0.3)
        return 0.4

class Motivator(RoleBase):
    factions = [Town]
    name = "Motivator"
    abilities = Townie.abilities + \
        [Ability(Voteop, name='motivate', args={'op':Voteop.Add})]
    def power(n, align):
        return 0.4

class Votethief(RoleBase):
    factions = [Town]
    name = "Vote Thief"
    abilities = Townie.abilities + \
        [Ability(Voteop, name='stealvote', args={'op':Voteop.Sub, 'trade':True})]
    def power(n, align):
        return 0.4

class Votegiver(RoleBase):
    factions = [Town]
    name = "Vote Giver"
    abilities = Townie.abilities + \
        [Ability(Voteop, name='givevote', args={'op':Voteop.Add, 'trade':True})]
    def power(n, align):
        return 0.4

class Tmpl:
    def __init__(self, role):
        self.basic = role.basic
        self.name = role.getname()
        self.factions = role.factions
        self.abilities = copy.deepcopy(role.abilities)

        self.role = role

        self.power = lambda n,align: role.power(n, align)

    def getname(self):
        return getattr(self, 'truename', self.name)

class TmplDay(Tmpl):
    def __init__(self, role):
        Tmpl.__init__(self, role)

        for abi in self.abilities:
            abi.phase = Day

        self.name = "Day "+role.name

        self.power = lambda n,align: role.power(n, align) + 0.2

class TmplOneShot(Tmpl):
    def __init__(self, role):
        Tmpl.__init__(self, role)

        for abi in self.abilities:
            if not abi.free:
                abi.uses = Some(1)

        self.name = "One-Shot "+role.name
        self.power = lambda n,align: max(role.power(n, align) - min(0.033333 * n - 0.1, 0.2), 0.1)
    
class TmplIncompetent(Tmpl):
    def __init__(self, role):
        Tmpl.__init__(self, role)

        for abi in self.abilities:
            if not abi.free:
                abi.resolvers=[Ability.RandomSecret()]

        self.truename = "Incompetent " + role.getname()

        self.power = lambda n,align: max(role.power(n, align) - 0.3, 0)

class TmplConfused(Tmpl):
    def __init__(self, role):
        Tmpl.__init__(self, role)

        abis = [x for x in self.abilities if not x.free]
        if len(abis) > 2:
            confabi = list(map(lambda x: x.getname(), abis))
            random.shuffle(confabi)
            for (conf, abi) in zip(confabi, abis):
                abi.name = conf

            self.truename = "Confused "+role.getname()

            self.power = lambda n,align: max(role.power(n, align) - 0.3, 0)

class TmplFail(Tmpl):
    def __init__(self, role, fail):
        Tmpl.__init__(self, role)
        self.fail = fail

        for abi in self.abilities:
            if not abi.free:
                abi.failure = fail

        self.truename = "%d%% %s"%(fail * 100, role.getname())

        self.power = lambda n,align: max(role.power(n, align) * self.fail, 0)

class TmplSanity(Tmpl):
    def __init__(self, role, sanity):
        Tmpl.__init__(self, role)

        for abi in self.abilities:
            abi.args['inspect'] = sanity

        self.name = role.name

        if sanity.name:
            self.truename = sanity.name + " " + role.getname()
        else:
            self.truename = role.getname()

        self.power = lambda n,align: max(role.power(n, align) - (0.1 if sanity.useful else 0.3), 0)

InsaneCop = TmplSanity(Cop, Insane())
NaiveCop = TmplSanity(Cop, Naive())
ParanoidCop = TmplSanity(Cop, Paranoid())
StonedCop = TmplSanity(Cop, Stoned())
RandomCop = TmplSanity(Cop, Random())

InsaneJoat = TmplSanity(Joat, Insane())
NaiveJoat = TmplSanity(Joat, Naive())
ParanoidJoat = TmplSanity(Joat, Paranoid())
StonedJoat = TmplSanity(Joat, Stoned())
RandomJoat = TmplSanity(Joat, Random())

InsaneStalker = TmplSanity(Stalker, Insane())
NaiveStalker = TmplSanity(Stalker, Naive())
ParanoidStalker = TmplSanity(Stalker, Paranoid())
StonedStalker = TmplSanity(Stalker, Stoned())
RandomStalker = TmplSanity(Stalker, Random())

OneShotBulletproof = TmplOneShot(Bulletproof)
OneShotRedirecter = TmplOneShot(Redirecter)
OneShotCop = TmplOneShot(Cop)
OneShotVig = TmplOneShot(Vigilante)
OneShotDayVig = TmplDay(OneShotVig)

DayCop = TmplDay(Cop)
DayVig = TmplDay(Vigilante)
DayDisabler = TmplDay(Disabler)

IncVig = TmplIncompetent(Vigilante)
IncCop = TmplIncompetent(Cop)
IncJoat = TmplIncompetent(Joat)
IncStalk = TmplIncompetent(Stalker)

ConfJoat = TmplConfused(Joat)
ConfStalk = TmplConfused(Stalker)

IncConfJoat = TmplIncompetent(TmplConfused(Joat))
IncConfStalk = TmplIncompetent(TmplConfused(Stalker))

HalfVig = TmplFail(Vigilante, 0.5)
FailVig = TmplFail(Vigilante, 0)

HalfCop = TmplFail(Cop, 0.5)
FailCop = TmplFail(Cop, 0)

HalfJoat = TmplFail(Joat, 0.5)
FailJoat = TmplFail(Joat, 0)

FailPGO = TmplFail(ParanoidGunOwner, 0)

def init():
    env = init.__globals__

    env['faction'] = {}
    for f in factions.values():
        env['faction'][f] = []

    env['roles'] = {}

    for k,v in list(filter(lambda t:
            (type(t[1]) is type
            and not t[1] is RoleBase
            and issubclass(t[1], RoleBase))
            or (isinstance(t[1], Tmpl)),
                env.items())):
        env['roles'][k] = v

        for fn, f in factions.items():
            if f in v.factions:
                env['faction'][f].append(v)

init()

def printroles():
    for k,v in faction.items():
        print(k.name, len(v), [x.getname() for x in v])

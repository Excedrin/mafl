from ability import Ability
from actions import *
from phase import *
from target import *
from sanity import *
from faction import *

class RoleBase:
    factions = [Town, Cult, Mafia, Sk, Survivor]

class Townie(RoleBase):
    def name():
        return "Townie"
    def setrole(actor):
        actor.addability(Ability(Vote, Day, free=True, public=True))

class Vigilante(RoleBase):
    factions = [Town, Sk]
    def name():
        return "Vigilante"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill))

class DayVigilante(RoleBase):
    factions = [Town, Sk]
    def name():
        return "Day Vigilante"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Day))

class OneShotVigilante(RoleBase):
    factions = [Town, Sk]
    def name():
        return "One Shot Vigilante"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, uses=1))

class OneShotDayVigilante(RoleBase):
    factions = [Town, Sk]
    def name():
        return "One Shot Day Vigilante"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Day, uses=1))

class GraveVigilante(RoleBase):
    factions = [Town, Survivor]
    def name():
        return "Grave Vigilante"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Any, uses=1, ghost=True))

class Cop(RoleBase):
    factions = [Town, Cult, Survivor]
    def name():
        return "Cop"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect))

class InsaneCop(RoleBase):
    factions = [Town, Cult, Survivor]
    def name():
        return "Cop"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, args={'sanity':Insane()}))

class NaiveCop(RoleBase):
    factions = [Town, Cult, Survivor]
    def name():
        return "Cop"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, args={'sanity':Naive()}))

class ParanoidCop(RoleBase):
    factions = [Town, Cult, Survivor]
    def name():
        return "Cop"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, args={'sanity':Paranoid()}))

class StonedCop(RoleBase):
    factions = [Town, Cult, Survivor]
    def name():
        return "Cop"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, args={'sanity':Stoned()}))

class RandomCop(RoleBase):
    factions = [Town, Cult, Survivor]
    def name():
        return "Cop"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, args={'sanity':Random()}))

class RoleCop(RoleBase):
    factions = [Town, Mafia]
    def name():
        return "Role Cop"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, args={'sanity':Rolecop()}))

class DevilsAdvocate(RoleBase):
    factions = [Sk]
    def name():
        return "Devil's Advocate"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, args={'sanity':Rolecop()}))
        actor.addability(Ability(Kill, Day))

class DayCop(RoleBase):
    factions = [Town]
    def name():
        return "Day Cop"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Day))

class OneShotCop(RoleBase):
    factions = [Town, Survivor]
    def name():
        return "One Shot Cop"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Any, uses=1))

class Doctor(RoleBase):
    factions = [Town, Cult, Survivor, Mafia]
    def name():
        return "Doctor"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Protect))

class BusDriver(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Bus Driver"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Bus))

class Roleblocker(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Roleblocker"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Block))

class Redirecter(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Redirecter"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Redirect))

class Tracker(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Tracker"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Track))

class Watcher(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Watcher"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Watch))

class NightWatchman(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Night Watchman"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Patrol))

class DoubleVoter(RoleBase):
    factions = [Town, Survivor]
    def name():
        return "Double Voter"
    def setrole(actor):
        actor.addability(Ability(Vote, Day, free=True, args={'maxvotes':2} ))

class NonVoter(RoleBase):
    factions = [Town]
    def name():
        return "Nonvoter"
    def setrole(actor):
        actor.addability(Ability(Vote, Day, free=True, args={'maxvotes':0} ))

class ParanoidGunOwner(RoleBase):
    factions = [Town, Survivor]
    def name():
        return "Paranoid Gun Owner"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Reflex, Any, auto=True, args={'action':Kill(0, [])} ))

class Eavesdropper(RoleBase):
    factions = [Town, Cult, Survivor, Mafia]
    def name():
        return "Eavesdropper"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Eavesdrop))

class Coward(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Coward"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Hide, uses=1, args={'target':Self}))

class Ascetic(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Ascetic"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Immune, args={'not':0,'immune':Kill(0,[])}))

class Bulletproof(RoleBase):
    factions = [Town, Mafia]
    def name():
        return "Bulletproof"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Immune, args={'immune':Kill(0,[])}))

class Commando(RoleBase):
    factions = [Town, Sk]
    def name():
        return "Commando"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Immune, Any, args={'immune':Kill(0,[])}))
        actor.addability(Ability(Kill))

class Delayer(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Delayer"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Delay, args={'phases':2}))

class Poisoner(RoleBase):
    factions = [Town, Survivor, Sk]
    def name():
        return "Poisoner"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Poison, Day))

class PoisonDoctor(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Poison Doctor"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Antidote))

class HumanShield(RoleBase):
    factions = [Town, Survivor, Mafia]
    def name():
        return "Human Shield"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Guard, args={'guard':Guard.Self}))

class Bodyguard(RoleBase):
    factions = [Town]
    def name():
        return "Bodyguard"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Guard))

class EliteBodyguard(RoleBase):
    factions = [Town]
    def name():
        return "Elite Bodyguard"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Guard, args={'guard':Guard.Other}))

class Friend(RoleBase):
    factions = [Town, Survivor]
    def name():
        return "Friend"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Friend, Day))

class Joat(RoleBase):
    factions = [Town]
    def name():
        return "Jack of all Trades"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, uses=1))
        actor.addability(Ability(Inspect, uses=1))
        actor.addability(Ability(Protect, uses=1))
        actor.addability(Ability(Block, uses=1))

class Stalker(RoleBase):
    factions = [Town]
    def name():
        return "Stalker"
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill))
        actor.addability(Ability(Inspect))

def init():
    env = init.__globals__

    env['faction'] = {}
    for f in factions.values():
        env['faction'][f] = []

    env['roles'] = {}

    for k,v in list(filter(lambda t:
            type(t[1]) is type
            and not t[1] is RoleBase
            and issubclass(t[1], RoleBase),
                env.items())):
        env['roles'][k] = v

        for fn, f in factions.items():
            if f in v.factions:
                env['faction'][f].append(v)

init()

def printroles():
    for k,v in faction.items():
        print(k.name, len(v), [x.name for x in v])

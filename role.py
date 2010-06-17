from ability import Ability
from actions import *
from phase import *
from target import *
from sanity import *

class RoleBase:
    pass

class Townie(RoleBase):
    def setrole(actor):
        actor.addability(Ability(Vote, Day, free=True, public=True))

class Vigilante(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Night))

class DayVigilante(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Day))

class OneShotVigilante(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Night, uses=1))

class GhostVigilante(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Any, uses=1, ghost=True))

class Cop(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night))

class InsaneCop(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Insane()}))

class NaiveCop(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Naive()}))

class ParanoidCop(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Paranoid()}))

class StonedCop(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Stoned()}))

class RandomCop(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Random()}))

class RoleCop(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Rolecop()}))

class DayCop(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Day))

class OneShotCop(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Any, uses=1))

class Doctor(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Protect, Night))

class BusDriver(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Bus, Night))

class Roleblocker(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Block, Night))

class Redirecter(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Redirect, Night))

class Tracker(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Track, Night))

class Watcher(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Watch, Night))

class NightWatchman(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Patrol, Night))

class DoubleVoter(RoleBase):
    def setrole(actor):
        actor.addability(Ability(Vote, Day, free=True, args={'maxvotes':2} ))

class NonVoter(RoleBase):
    def setrole(actor):
        actor.addability(Ability(Vote, Day, free=True, args={'maxvotes':0} ))

class ParanoidGunOwner(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Reflex, Any, auto=True, args={'action':Kill(0, [])} ))

class Eavesdropper(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Eavesdrop, Night))

class Coward(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Hide, Night, uses=1, args={'target':Self}))

class Ascetic(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Immune, Night, args={'not':0,'immune':Kill(0,[])}))

class Bulletproof(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Immune, Night, args={'immune':Kill(0,[])}))

class Delayer(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Delay, Night, args={'phases':2}))

class Poisoner(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Poison, Day))

class PoisonDoctor(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Antidote, Night))

class HumanShield(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Guard, Night, args={'guard':mafl.Self}))

class Bodyguard(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Guard, Night))

class EliteBodyguard(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Guard, Night, args={'guard':mafl.Other}))

class Friend(RoleBase):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Friend, Day))

def init():
    env = init.__globals__
    env['roles'] = {}
    for k,v in list(filter(lambda t:
            type(t[1]) is type
            and not t[1] is RoleBase
            and issubclass(t[1], RoleBase),
                env.items())):
        env['roles'][k] = v

init()

from ability import Ability
from actions import *
from phase import *
from target import *
from sanity import *

class Role:
    pass

class Townie(Role):
    def setrole(actor):
#        Role.setrole(actor)
        actor.addability(Ability(Vote, Day, free=True, public=True))

class Vigilante(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Night))

class DayVigilante(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Day))

class OneShotVigilante(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Kill, Night, uses=1))

class Cop(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night))

class InsaneCop(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Insane()}))

class NaiveCop(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Naive()}))

class ParanoidCop(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Paranoid()}))

class StonedCop(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Stoned()}))

class RandomCop(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Random()}))

class RoleCop(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Night, args={'sanity':Rolecop()}))

class DayCop(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Day))

class OneShotCop(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Inspect, Any, uses=1))

class Doctor(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Protect, Night))

class BusDriver(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Bus, Night))

class Roleblocker(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Block, Night))

class Redirecter(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Redirect, Night))

class Tracker(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Track, Night))

class Watcher(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Watch, Night))

class NightWatchman(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Patrol, Night))

class DoubleVoter(Role):
    def setrole(actor):
#        Role.setrole(actor)
        actor.addability(Ability(Vote, Day, free=True, args={'maxvotes':2} ))

class NonVoter(Role):
    def setrole(actor):
#        Role.setrole(actor)
        actor.addability(Ability(Vote, Day, free=True, args={'maxvotes':0} ))

class ParanoidGunOwner(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Reflex, Any, auto=True, args={'action':Kill(0, [])} ))

class Eavesdropper(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Eavesdrop, Night))

class Coward(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Hide, Night, uses=1, args={'target':Self}))

class Ascetic(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Immune, Night, args={'not':0,'immune':Kill(0,[])}))

class Godfather(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Immune, Night, args={'immune':Kill(0,[])}))

class Delayer(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Delay, Night, args={'phases':2}))

class Poisoner(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Poison, Day))

class PoisonDoctor(Role):
    def setrole(actor):
        Townie.setrole(actor)
        actor.addability(Ability(Antidote, Night))

def init():
    env = init.__globals__
    env['roles'] = {}
    for k,v in list(filter(lambda t:
            type(t[1]) is type
            and not t[1] is Role
            and issubclass(t[1], Role),
                env.items())):
        env['roles'][k] = v

init()

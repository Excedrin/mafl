from ability import Ability
from actions import *
from phase import *

class Role:
    def setrole(self, actor):
        actor.role = self

class Townie(Role):
    def setrole(self, actor):
        Role.setrole(self, actor)
        actor.addability(Ability(Vote, Day, free=True))

class Vigilante(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Kill, Night))

class DayVigilante(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Kill, Day))

class OneShotVigilante(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Kill, Night, uses=1))

class Cop(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Inspect, Night))

class DayCop(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Inspect, Day))

class OneShotCop(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Inspect, Night, uses=1))

class Doctor(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Protect, Night))

class BusDriver(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Bus, Night))

class Roleblocker(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Block, Night))

class Redirecter(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Redirect, Night))

class Tracker(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Track, Night))

class Watcher(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Watch, Night))

class NightWatchman(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Patrol, Night))

class DoubleVoter(Townie):
    def setrole(self, actor):
        Role.setrole(self, actor)
        actor.addability(Ability(Vote, Day, free=True, args=[2] ))

class NonVoter(Townie):
    def setrole(self, actor):
        Role.setrole(self, actor)
        actor.addability(Ability(Vote, Day, free=True, args=[0] ))

class ParanoidGunOwner(Townie):
    def setrole(self, actor):
        Role.setrole(self, actor)
        actor.addability(Ability(Reflex, Any, auto=True, args=[Kill(0, [])] ))

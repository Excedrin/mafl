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

class Doctor(Townie):
    def setrole(self, actor):
        Townie.setrole(self, actor)
        actor.addability(Ability(Protect, Night))

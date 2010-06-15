class Phase:
    name = "unknown"
    instant = True
    nextphase = None
    started = False

Phase.nextphase = Phase

class Day(Phase):
    name = "day"
    instant = True
    nextphase = None
    started = True

class Night(Phase):
    name = "night"
    instant = False
    nextphase = Day
    started = True

Day.nextphase = Night

class Any(Day, Night):
    name = "any"

class Signups(Phase):
    name = "signups"
    instant = True
    nextphase = Day

class Idle(Phase):
    name = "idle"
    instant = True
    nextphase = Signups

class Done(Phase):
    name = "done"
    instant = True
    nextphase = Idle

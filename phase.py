class Phase:
    name = "unknown"
    instant = True
    nextphase = None

Phase.nextphase = Phase

class Day(Phase):
    name = "day"
    instant = True
    nextphase = None

class Night(Phase):
    name = "night"
    instant = False
    nextphase = Day

Day.nextphase = Night

class Starting(Phase):
    name = "starting"
    instant = True
    nextphase = Day

class Any(Day, Night):
    pass

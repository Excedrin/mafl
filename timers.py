import time
from misc import Some

class Timers:
    def __init__(self):
        self.timers = {}
   
    def settimer(self, name, duration):         
        self.timers[name] = time.time() + duration

    def setfirst(self, name, duration):         
        if not name in self.timers:
            self.settimer(name, duration)

    def remaining(self, name):
        if name in self.timers:
            timer = self.timers[name]
            return Some(int(timer - time.time()))
        else:
            return None

    def expired(self, name):
        remain = self.remaining(name)
        if remain:
            return remain.v < 0
        else:
            return False

    def dec(self, name):
        if name in self.timers:
            self.timers[name] -= 1

    def remove(self, name):
        if name in self.timers:
            del self.timers[name]

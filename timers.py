import time

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
            return int(timer - time.time())
        else:
            return 0

    def expired(self, name):
        return self.remaining(name) < 0

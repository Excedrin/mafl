class Ability:
    def __init__(self, action, phase, uses=None, free=False, args=[]):
        self.action = action
        self.phase = phase
        self.uses = uses
        self.used = False
        self.free = free
        self.args = args

    def __str__(self):
        return("ability: %s %s %s %s" %(self.action.name, self.phase, self.uses, self.used))

    def reset(self):
        self.used = False

    def use(self, state, player, targets):
        err = ""
        if not self.free and self.used:
            err = "%s has already been used" % self.action.name
        elif not self.free and self.uses and self.uses < 1:
            err = "%s has no uses left" % self.action.name
        elif not issubclass(self.phase, state.phase):
            err = "%s can't be used during this phase" % self.action.name
        else:
            self.used = True
            if not self.free and self.uses:
                self.uses -= 1
            slots = [state.slotbyname(x) for x in targets]
            actor = state.slotbyplayer(player)
            state.enqueue(self.action(actor, slots, self.args))
            return (True, "confirmed")
        return (False, err)

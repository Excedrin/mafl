import target

class Ability:
    def __init__(self, action, phase, uses=None, free=False, auto=False, args={}):
        self.action = action
        self.phase = phase
        self.uses = uses
        self.used = False
        self.free = free
        self.auto = auto
        self.args = args

    def __str__(self):
        # instantiate an action to get it to format itself
        desc = [str(self.action(0,[],self.args)), "(%s phase)" % self.phase.name]
        if self.auto:   
            desc.insert(0, "auto")

        if self.uses:
            desc.insert(0, "%d use" % self.uses)
        return(" ".join(desc))

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
            if not self.free:
                self.used = True
                if self.uses:
                    self.uses -= 1

            actor = state.slotbyplayer(player)

            targetresolver = self.args.get('targets', target.Target)
            slots = targetresolver.gettargets(state, actor, targets)

            state.enqueue(self.action(actor, slots, self.args))

            return (True, "%s confirmed"%(self.action.name))
        return (False, err)

    def useauto(self, phase, player):
        if self.auto and issubclass(self.phase, phase):
            return self.action(player, [player], self.args)
        else:
            return None

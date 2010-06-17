import target

class Ability:
    def __init__(self, action, phase, uses=None, free=False, auto=False, public=False, args={}):
        self.action = action
        self.phase = phase
        self.uses = uses
        self.used = False
        self.free = free
        self.auto = auto
        self.args = args
        self.public = public

# it's the right phase, and (an unused action, with uses left, or a free action)
    def usable(self, state):
        return (issubclass(self.phase, state.phase)
                and ((not self.used
                      and (self.uses == None
                          or self.uses > 0)
                      and not self.auto)
                    or self.free))

    def __str__(self):
        # instantiate an action to get it to format itself
        desc = [str(self.action(0,[],self.args)), "(%s phase)" % self.phase.name]
        if self.auto:   
            desc.insert(0, "auto")

        if self.uses != None:
            desc.insert(0, "%d use" % self.uses)
        return(" ".join(desc))

    def reset(self):
        self.used = False

    def use(self, state, public, player, targets):
        if self.public != public:
            err = "%s must be used %s" % (self.action.name,
                "publicly" if self.public else "privately")
        elif self.auto:
            err = "%s is an auto action" % self.action.name
        elif not self.free and self.used:
            err = "%s has already been used" % self.action.name
        elif not self.free and self.uses != None and self.uses < 1:
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

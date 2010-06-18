import target
import phase

class Ability:
    class Dead:
        desc = "dead"
        def test(actor, x, state):
            return not state.playerbyslot(x).living
    class Living:
        desc = "living"
        def test(actor, x, state):
            return state.playerbyslot(x).living
    class NonSelf:
        desc = "other than yourself"
        def test(actor, x, state):
            return actor != x

    def __init__(self, action, phase=phase.Night, uses=None, free=False, auto=False, public=False, ghost=False, restrict=[Living, NonSelf], args={}):
        self.action = action
        self.phase = phase
        self.uses = uses
        self.used = False
        self.free = free
        self.auto = auto
        self.args = args
        self.public = public
        self.ghost = ghost
        self.restrict = restrict

# it's the right phase, and (an unused action, with uses left, or a free action)
    def usable(self, player, state):
        return (issubclass(self.phase, state.phase)
                and ((not self.used
                      and (not self.uses or self.uses > 0)
                      and not self.auto
                      and player.living ^ self.ghost)
                    or self.free))

    def __str__(self):
        # instantiate an action to get it to format itself
        desc = [str(self.action(0,[],self.args)), "(%s phase)" % self.phase.name]
        if self.auto:   
            desc.insert(0, "auto")
        if self.ghost:   
            desc.insert(0, "ghost")

        if self.uses:
            desc.insert(0, "%d use" % self.uses.v)
        return(" ".join(desc))

    def reset(self):
        self.used = False

    def use(self, state, public, player, targets):
        if self.action.arity and len(targets) != self.action.arity.v:
            err = "%s needs %d target(s) (%s)" %(self.action.name,self.action.arity,', '.join(targets))
        elif not player.living and not self.ghost:
            err = "%s isn't usable when dead"%(self.action.name)
        elif self.ghost and player.living:
            err = "%s isn't usable when alive"%(self.action.name)
        elif self.public != public:
            err = "%s must be used %s" % (self.action.name,
                "publicly" if self.public else "privately")
        elif self.auto:
            err = "%s is an auto action" % self.action.name
        elif not self.free and self.used:
            err = "%s has already been used" % self.action.name
        elif not self.free and self.uses and self.uses < 1:
            err = "%s has no uses left" % self.action.name
        elif not issubclass(self.phase, state.phase):
            err = "%s can't be used during this phase" % self.action.name
        else:
            actor = state.slotbyplayer(player)

            targetresolver = self.args.get('targets', target.Target)
            slots = targetresolver.gettargets(state, actor, targets)

            if self.restrict:
                for test in self.restrict:
                    if not all([test.test(actor, x, state) for x in slots]):
                        return (False, "%s needs %s target(s) (%s)" %(self.action.name, test.desc, ', '.join(targets)))

            # finally good to go

            if not self.free:
                self.used = True
                if self.uses:
                    self.uses -= 1

            state.enqueue(self.action(actor, slots, self.args))

            return (True, "%s confirmed (%s)"%(self.action.name,', '.join(targets)))
        return (False, err)

    def useauto(self, phase, player):
        if self.auto and issubclass(self.phase, phase):
            return self.action(player, [player], self.args)
        else:
            return None

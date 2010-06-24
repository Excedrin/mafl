import phase
import faction

class Ability:
# fixed targets
    class User: # user specified target
        forced = False
        def gettargets(self, state, actor, target, slots):
            return [state.slotbyname(target)]

    class Self:
        forced = True
        def gettargets(self, state, actor, target, slots):
            return [actor]

    class Everyone:
        forced = True
        def gettargets(self, state, actor, target, slots):
            return [x for x in state.livingslots()]

    class EveryoneElse:
        forced = True
        def gettargets(self, state, actor, target, slots):
            return [x for x in state.livingslots() if x != actor]

    class Random:
        forced = True
        def gettargets(self, state, actor, target, slots):
            everyone = Ability.Everyone.gettargets(self, state, actor, target, slots)
            return [state.rng.choice(everyone)]

    class RandomNonSelf:
        forced = True
        def gettargets(self, state, actor, target, slots):
            nonself = Ability.EveryoneElse.gettargets(self, state, actor, target, slots)
            return [state.rng.choice(nonself)]

    # secretly replace target w/random target
    class RandomSecret(Random):
        forced = False

    class ArgN:
        forced = True
        def __init__(self, n):
            self.n = n
        def gettargets(self, state, actor, target, slots):
            return [slots[self.n]]

# target restrictions
    class Dead:
        desc = "dead"
        def test(actor, x, state):
            return not state.playerbyslot(x).living
    class Living:
        desc = "living"
        def test(actor, x, state):
            return state.playerbyslot(x).living
    class LivingOrNL:
        desc = "living"
        def test(actor, x, state):
            p = state.playerbyslot(x)
            return p.living or p.name == 'nolynch'
    class NonSelf:
        desc = "other than yourself"
        def test(actor, x, state):
            return actor != x
    # these two restrictions require the player acting is on an informed minority team
    class NonTeam:
        desc = "unaligned"
        def test(actor, x, state):
            p1 = state.playerbyslot(actor)
            p2 = state.playerbyslot(x)
            if isinstance(p1.faction, faction.Mafia) or isinstance(p1.faction, faction.Cult):
                return p1.faction != p2.faction
            else:
                return True
    class SameTeam:
        desc = "aligned"
        def test(actor, x, state):
            p1 = state.playerbyslot(actor)
            p2 = state.playerbyslot(x)
            if isinstance(p1.faction, faction.Mafia) or isinstance(p1.faction, faction.Cult):
                return p1.faction == p2.faction
            else:
                return True

    def __init__(self, action, phase=phase.Night, uses=None,
                    free=False, auto=False, public=False, ghost=False,
                    restrict=[Living, NonSelf], failure=0, name=None, 
                    resolvers=[User()], optargs=False, untrackable=False, args={}):

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
        self.failure = failure

        self.resolvers = resolvers
        self.optargs = optargs

        self.untrackable = untrackable

        self.currentaction = None

        if name:
            self.name = name
        else:
            self.name = action.name

        if auto:
            for resolver in self.resolvers:
                if not resolver.forced:
                    raise ValueError

    def getname(self):
        return self.name

# it's the right phase, and (an unused action, with uses left, or a free action)
    def usable(self, player, state):
        return (issubclass(self.phase, state.phase)
                and ((not self.used
                      and (not self.uses or self.uses.v > 0)
                      and not self.auto
                      and player.living ^ self.ghost)
                    or self.free))

    def __str__(self):
        # instantiate an action to get it to format itself
        act = self.action(0, [], self.args, rename=self.getname())
        desc = [str(act), "(%s phase)" % self.phase.name]
        if self.auto:   
            desc.insert(0, "auto")
        if self.ghost:   
            desc.insert(0, "ghost")

        if self.uses:
            desc.insert(0, "%d use" % self.uses.v)
        return(" ".join(desc))

    def reset(self):
        self.used = False

    def resolvetargets(self, state, actor, targets, slots):
        resolved = []
        # handle possibly forced targets
        tmp = list(targets)
        tmp.extend(["" for _ in range(len(self.resolvers))])
        for resolver in self.resolvers:
            target = tmp.pop(0)
            resolved.extend(resolver.gettargets(state, actor, target, slots))

        print("resolved",resolved)
        return resolved

    def use(self, state, public, player, targets):
        name = self.getname()

        if not player.living and not self.ghost:
            err = "%s isn't usable when dead"%(name)
        elif self.ghost and player.living:
            err = "%s isn't usable when alive"%(name)
        elif self.public != public:
            err = "%s must be used %s" % (name,
                "publicly" if self.public else "privately")
        elif self.auto:
            err = "%s is an auto action" % name
        elif not self.free and self.used:
            err = "%s has already been used" % name
        elif not self.free and self.uses and self.uses.v < 1:
            err = "%s has no uses left" % name
        elif not issubclass(self.phase, state.phase):
            err = "%s can't be used during this phase" % name
        else:
            actor = state.slotbyplayer(player)

            if not self.optargs:
                arity = len(list(filter(lambda x: not x.forced, self.resolvers)))
                print("arity",arity)
                if len(targets) != arity:
                    err = "%s needs %d target(s) (%s)" %(name, arity,
                                                    ', '.join(targets))
                    return (False, err)

            # initially use slots that user specified
            slots = [state.slotbyname(x) for x in targets]

            # check target restrictions
            if self.restrict:
                for test in self.restrict:
                    if not all([test.test(actor, x, state) for x in slots]):
                        err = "%s needs %s target(s) (%s)" %(name, test.desc, ', '.join(targets))
                        return (False, err)

            resolved = self.resolvetargets(state, actor, targets, slots)

            # finally good to go
            if not self.free:
                self.used = True
                if self.uses:
                    self.uses.v -= 1

            # don't enqueue it if it fails
            if state.rng.random() > self.failure:
                self.currentaction = self.action(actor, resolved, self.args)
                state.enqueue(self.currentaction)

            return (True, "%s (%s) confirmed"%(name,', '.join(targets)))
        return (False, err)

    def useauto(self, state, phase, actor):
        if self.auto and issubclass(self.phase, phase):
            if state.rng.random() <= self.failure:
                return None
            
            if self.uses and self.uses.v > 0:
                if self.currentaction and self.currentaction.used:
                    self.uses.v -= 1
                if self.uses.v <= 0:
                    return None
            else:
                return None

            resolved = self.resolvetargets(state, actor, [], [])
            print("useauto",actor,resolved,self.uses)
            self.currentaction = self.action(actor, resolved, self.args)
            return self.currentaction
        else:
            return None

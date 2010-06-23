from mafqueue import Mqueue
import faction
import sanity
from misc import Some
import copy

class ActionBase:
    name = "none"
    priority = 99999999

    untrackable = False
    noimmune = False
    notrigger = False

    def __init__(self, actor, targets, args={}, rename=None):
        self.actor = actor
        self.targets = targets
        self.args = copy.deepcopy(args)
        if rename:
            self.name = rename

        if 'untrackable' in args:
            self.untrackable = args['untrackable']
        for k,v in args.items():
#            print("action set from args",k,v)
            self.__dict__[k] = v

    def __lt__(self, other):
        return self.__class__.priority < other.__class__.priority

    def getname(self):
        return self.name

    def __str__(self):
        return self.getname()
#        return("Action: %s %s %s" % (self.actor, self.__class__.name, self.targets))

    def resolve(self, state):
        return state.queue

class Action(ActionBase):
    pass

class Message(Action):
    name = "message"
    priority = 100

    untrackable = True

    def resolve(self, state):
        if 'msg' in self.args:
            for slot in self.targets:
                msg = self.args['msg']
                state.messageslot(slot, msg)
                print("message from %s to %s: %s" % (self.actor, slot, msg))

        return state.queue

# priority here probably doesn't matter since it's going to be a day ability usually
class Vote(Action):
    name = "vote"
    priority = 99

    untrackable = True
    noimmune = True
    notrigger = True

    def resolve(self, state):
        state.resolved(self)

        player = state.playerbyslot(self.actor)

        maxvotes = 1
        if 'maxvotes' in self.args:
            maxvotes = self.args['maxvotes']
        state.vote(self.actor, self.targets[0:maxvotes])

        return state.queue

class Alter(Action):
    name = "alter"
    priority = 19

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            for act in state.queue:
                if isinstance(act, Inspect) and target in act.targets:
                    if isinstance(act.inspect, sanity.Sane):
                        act.inspect = sanity.Insane(act.inspect.factions)
                    elif isinstance(act.inspect, sanity.Insane):
                        act.inspect = sanity.Sane(act.inspect.factions)

        return state.queue

class Inspect(Action):
    name = "inspect"
    priority = 20
    inspect = sanity.Sane([faction.Mafia, faction.Town])

    def resolve(self, state):
        state.resolved(self)

        for slot in self.targets:
            target = state.playerbyslotbus(slot)

            msg = target.name+" "+self.inspect.result(target)
            state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))

        return state.queue

class Kill(Action):
    name = "kill"
    priority = 70
    how = "was killed"

    def resolve(self, state):
        state.resolved(self)

        for slot in self.targets:
            player = state.playerbyslotbus(slot)
            if player.living:
                player.living = False
                print("kill resolved (%s killed by %s)" % (player.name, self.actor))
                state.message(None, "%s (%s) %s"%(player.name, player.flip(), self.how))
                state.resetvotes()

        return state.queue

class SuperKill(Action):
    name = "superkill"
    priority = 70

    def resolve(self, state):
        return Kill.resolve(self, state)

class Lynch(ActionBase):
    name = "lynch"
    priority = 70
    how = "was killed"

    def resolve(self, state):
        state.votecount(True)
        return Kill.resolve(self, state)

class Suicide(Action):
    name = "suicide"
    priority = 70
    how = "comitted suicide"

    noimmune = True
    notrigger = True

    def resolve(self, state):
        self.targets = [self.actor]
        return Kill.resolve(self, state)

# resolve earlier than hide
class PoisonKill(Action):
    name = "poisonkill"
    priority = 10
    how = "was poisoned"

    notrigger = True

    def resolve(self, state):
        return Kill.resolve(self, state)

class Poison(Action):
    name = "poison"
    priority = 70
    phases = 2

    notrigger = True

    def resolve(self, state):
        state.resolved(self)

        delayedact = PoisonKill(0, self.targets)
        state.delay(self.phases, delayedact)

        return state.queue

class Recruit(Action):
    name = "recruit"
    priority = 75

    def resolve(self, state):
        state.resolved(self)
        actor = state.playerbyslot(self.actor)

        for slot in self.targets:
            player = state.playerbyslotbus(slot)
            player.faction = actor.faction

            state.message(player.name, player.fullrolepm(state))
            state.resetvotes()

        return state.queue

class Copy(Action):
    name = "copy"
    priority = 10

    def resolve(self, state):
        state.resolved(self)

        source = self.targets[0]
        dest = self.targets[1]
#        print("copy src: %s dst: %s" %(source,dest))

        newqueue = Mqueue()
        for act in state.queue:
            if act.actor == source:
                newact = copy.deepcopy(act)
                newact.actor = source
                newact.targets[0] = dest
#                print("newact:",newact)
                newqueue.enqueue(newact)
            newqueue.enqueue(act)
        return newqueue

# bus swaps two player's seating assignments
# if a and b are bussed, everything that would affect a now affects b
# and vice versa

# unlike redirect,
# inspections and results that include a target's name should still have
# the actual name

class Bus(Action):
    name = "bus"
    priority = 12

    def resolve(self, state):
        state.resolved(self)

        source = self.targets[0]
        dest = self.targets[1]

        if source in state.bus:
            state.bus[source].append(dest)
        else:
            state.bus[source] = [dest]
        if dest in state.bus:
            state.bus[dest].append(source)
        else:
            state.bus[dest] = [source]
#        print("state.bus",state.bus)

        return state.queue

class Delay(Action):
    name = "delay"
    priority = 13

    phases = 1

    def resolve(self, state):
        state.resolved(self)

        newqueue = Mqueue()
        for act in state.queue:
            if act.actor in [state.bussedslot(x) for x in self.targets]:
                if act.args.get('delayed', False):
                    newqueue.enqueue(act)
                else:
                    delayedact = copy.deepcopy(act)
                    delayedact.args['delayed'] = True
                    state.delay(self.phases, delayedact)
            else:
                newqueue.enqueue(act)

        return newqueue

class Block(Action):
    name = "block"
    priority = 14

    def resolve(self, state):
        state.resolved(self)
        newqueue = Mqueue()

        for act in state.queue:
            if not act.actor in [state.bussedslot(x) for x in self.targets]:
                newqueue.enqueue(act)
            # blocked actions don't go into resqueue

        return newqueue

class Eavesdrop(Action):
    name = "eavesdrop"
    priority = 95
    untrackable = True

    def resolve(self, state):
        state.resolved(self)
        newqueue = Mqueue()
        for act in state.queue:
            for target in self.targets:
                if isinstance(act, Message) and target in act.targets:
                    newact = copy.deepcopy(act)
                    newact.targets = [self.actor]
                    newqueue.enqueue(newact)
            newqueue.enqueue(act)
        return newqueue

class Friend(Action):
    name = "friend"
    priority = 20

    def resolve(self, state):
        state.resolved(self)
        actor = state.playerbyslot(self.actor)

        msg = "%s is %s" % (actor.name, actor.faction.name)
        for target in state.fix(self.targets):
            state.enqueue(Message(self.actor, [target], {'msg':msg}))

        return state.queue

class Guard(Action):
    class Both:
        name = "(you die in place of target and attacker dies)"
    class Other:
        name = "(attacker dies)"
    class Self:
        name = "(you die in place of target)"

    name = "guard"
    priority = 40

    guard = Guard.Both

    def resolve(self, state):
        state.resolved(self)

        killfound = False
        for target in self.targets:
            newqueue = Mqueue()
            for act in state.queue:
                if killfound or (not (isinstance(act, Kill) and target in act.targets)):
                    newqueue.enqueue(act)
                else:
                    if self.guard is Both or self.guard is Other:
                        # bodyguard kills the killer (ignore bus)
                        newqueue.enqueue(Kill(self.actor, [act.actor]))
                    if self.guard is Both or self.guard is Self:
                        # bodyguard dies also / instead of target
                        newqueue.enqueue(Kill(act.actor, [self.actor]))
                    killfound = True
        return newqueue

    def __str__(self):
        msg = [self.getname(), self.guard.name]
        return " ".join(msg)

# uses two keys in args:
# 'immune' a list of classes that this action will nullify
# 'not' reverse the comparison (immunity is susceptibility)

# immune means you're immune to the action(s) in the list
# example would be Godfather, which is immune to kills

# not immune means you're immune to everything except subclasses of the listed action
# an example would be Ascetic, which is immune to all actions except kills
class Immune(Action):
    name = "immune"
    priority = 9
    immune = []

    def resolve(self, state):
        state.resolved(self)

        if 'not' in self.args:
            operator = lambda x: not x
        else:
            operator = lambda x: x

        newqueue = Mqueue()
        for act in state.queue:
            for target in self.targets:
                if target in act.targets:
                    for immuneact in self.immune:
                        if act.noimmune:
                            newqueue.enqueue(act)
                        elif operator(isinstance(act, immuneact)):
                            state.resqueue.enqueue(act)
                        else:
                            newqueue.enqueue(act)
                else:
                    newqueue.enqueue(act)

        return newqueue

    def __str__(self):
        msg = [self.getname()]
        if 'not' in self.args:
            msg.insert(0, 'not')
        msg.append(", ".join([x.name for x in self.immune]))
        return " ".join(msg)

class Reflex(Action):
    name = "reflex"
    priority = 8
    triggers = [Action]
    action = None

    notrigger = True
    noimmune = True

    def resolve(self, state):

        newacts = []
        for target in self.targets:
            for act in state.queue + state.resqueue:
                if act.actor != self.actor and target in act.targets:
                    for trigger in self.triggers:
                        if not act.notrigger and isinstance(act, trigger):
                            if not self.action:
                                reflexact = act
                            else:
                                reflexact = self.action
                            newact = copy.deepcopy(reflexact)
                            newact.actor = target
                            newact.targets = [act.actor]
                            newacts.append(newact)

        resolved = False
        for newact in newacts:
            state.enqueue(newact)
            resolved = True

        if resolved:
            state.resolved(self)
        elif not isinstance(self, Reflex2):
            newreflex = copy.deepcopy(self)
            newreflex.__class__ = Reflex2
            print("enqueue newreflex",newreflex)
            state.enqueue(newreflex)

        return state.queue

    def __str__(self):
        msg = [self.getname()]
        if 'action' in self.args:
            msg.append(self.args['action'].name)
        return " ".join(msg)

class Reflex2(Reflex):
    priority = 101

class Hide(Action):
    name = "hide"
    priority = 11

    def resolve(self, state):
        state.resolved(self)

        newqueue = Mqueue()
        for target in self.targets:
            # all actions targeting a hidden player fail
            for act in state.queue:
                if act.targets[0] != target:
                    newqueue.enqueue(act)
        return newqueue

class Protect(Action):
    name = "protect"
    priority = 50

    def resolve(self, state):
        state.resolved(self)

        killfound = False
        newqueue = Mqueue()

        for target in self.targets:
            for act in state.queue:
                if killfound or (not (isinstance(act, Kill) and target in act.targets)):
                    newqueue.enqueue(act)
                else:
                    killfound = True
#                    print("kill %s canceled by protect" % act.targets)
                    state.resolved(act)

        return newqueue

class Antidote(Action):
    name = "antidote"
    priority = 50

    def resolve(self, state):
        state.resolved(self)

        killfound = False
        newqueue = Mqueue()

        for target in self.targets:
            for act in state.queue:
#            for (phase, act) in state.delayqueue:
                if killfound or (not (isinstance(act, PoisonKill) and target in act.targets)):
                    newqueue.enqueue(act)
#                    newqueue.enqueue((phase, act))
                else:
                    killfound = True

#        if killfound:
#            state.delayqueue = newqueue

        return newqueue

class Redirect(Action):
    name = "redirect"
    priority = 15

    def resolve(self, state):
        state.resolved(self)

        source = self.targets[0]
        dest = self.targets[1]

        newqueue = Mqueue()
        for act in state.queue:
            # don't redirect self targeted actions
            if act.actor == source and act.targets[0] != act.actor:
                newact = copy.deepcopy(act)
                newact.targets[0] = dest
#                print("newact:",newact)
                newqueue.enqueue(newact)
            else:
                newqueue.enqueue(act)
        return newqueue

class Track(Action):
    name = "track"
    priority = 90

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            bussed = state.bussedslot(target)
            targets = []
            for act in state.queue + state.resqueue:
                if not act.untrackable and act.actor == bussed:
                    targets.extend(act.targets)

            if targets:
                res = ", ".join([state.playerbyslot(x).name for x in state.fix(targets)]) 
            else:
                res = "nobody"
            msg = "%s targeted %s" % (state.playerbyslot(bussed).name, res)
            state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))

        return state.queue

class Watch(Track):
    name = "watch"
    priority = 90

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            bussed = state.bussedslot(target)
            acted = False
            for act in state.queue + state.resqueue:
                if not act.untrackable and act.actor == bussed:
                    acted = True
                    break

            result = "used an ability" if acted else "didn't use an ability"

            msg = "%s %s" % (state.playerbyslot(bussed).name, result)

            state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))

        return state.queue

class Patrol(Track):
    name = "patrol"
    priority = 90

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            bussed = state.bussedslot(target)
            fakename = state.playerbyslot(target).name
            actors = []

            for act in state.queue + state.resqueue:
                if not isinstance(act, Patrol) and not act.untrackable and bussed in state.fix(act.targets):
                    actors.append(act.actor)

            if actors:
                res = ", ".join([state.playerbyslot(x).name for x in actors])
            else:
                res = "nobody"

            msg = "%s was targeted by %s" % (fakename, res)

            state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))

        return state.queue

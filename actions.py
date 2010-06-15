from mafqueue import Mqueue

import copy

class Untrackable:
    pass

class Action:
    name = "none"
    priority = 99999999

    def __init__(self, actor, targets, args=[]):
        self.actor = actor
        self.targets = targets
        self.args = args

    def __lt__(self, other):
        return self.__class__.priority < other.__class__.priority

    def __str__(self):
        return("Action: %s %s %s" % (self.actor, self.__class__.name, self.targets))

    def resolve(self, state):
        return state.queue

class Message(Action, Untrackable):
    name = "message"
    priority = 100

    def resolve(self, state):
        for slot in self.targets:
            msg = ''.join(self.args)
            state.messageslot(slot, msg)
            print("message from %s to %s: %s" % (self.actor, slot, self.args))

        return state.queue

class Vote(Action, Untrackable):
    name = "vote"
    priority = 99

    def resolve(self, state):
        state.resolved(self)

        player = state.playerbyslot(self.actor)

        maxvotes = 1
        if self.args:
            maxvotes = self.args[0]
        state.vote(self.actor, self.targets[0:maxvotes])

        return state.queue

class Inspect(Action):
    name = "inspect"
    priority = 20

    def resolve(self, state):
        state.resolved(self)

        for slot in self.targets:
            target = state.playerbyslotbus(slot)
            align = target.faction.name

            msg = "%s is %s" % (target.name, align)
            state.queue.enqueue(Message(self.actor, [self.actor], [msg]))

        return state.queue

class Kill(Action):
    name = "kill"
    priority = 70

    def resolve(self, state):
        state.resolved(self)

        for slot in self.targets:
            player = state.playerbyslotbus(slot)
            player.living = False
            print("kill resolved (%s killed by %s)" % (player.name, self.actor))
            how = "killed"
            if self.args:
                how = self.args[0]
            state.message(None, "%s (%s) was %s"%(player.name, player.flip(), how))
            state.resetvotes()

        return state.queue

class Lynch(Kill):
    name = "lynch"
    priority = 70

    def resolve(self, state):
        state.resolved(self)

        for slot in self.targets:
            player = state.playerbyslot(slot)
            player.living = False
            print("lynch resolved (%s killed by %s)" % (player.name, self.actor))
            how = "lynched"
            if self.args:
                how = self.args[0]
            state.message(None, "%s (%s) was %s"%(player.name, player.flip(), how))
            state.votecount(True)
            state.resetvotes()

        return state.queue

class Block(Action):
    name = "block"
    priority = 13

    def resolve(self, state):
        newqueue = Mqueue()

        for act in state.queue:
            if not act.actor in [state.bussedslot(x) for x in self.targets]:
                newqueue.enqueue(act)
            # blocked actions don't go into resqueue

        state.resolved(self)
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

class Eavesdrop(Action, Untrackable):

    name = "eavesdrop"
    priority = 95

    def resolve(self, state):
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
            state.queue.enqueue(Message(self.actor, [target], [msg]))

        return state.queue

class Guard(Action):

    name = "guard"
    priority = 40

    def resolve(self, state):
        state.resolved(self)

        killfound = False
        for target in self.targets:
            newqueue = Mqueue()
            for act in state.queue:
                if killfound or (not (isinstance(act, Kill) and target in act.targets)):
                    newqueue.enqueue(act)
                else:
                    # bodyguard kills the killer (ignore bus)
                    newqueue.enqueue(Kill(self.actor, [act.actor]))
                    # bodyguard dies instead of target
                    newqueue.enqueue(Kill(act.actor, [self.actor]))
                    killfound = True
        return newqueue

class Immune(Action):

    name = "immune"
    priority = 8

    def resolve(self, state):
        state.resolved(self)

        newqueue = Mqueue()
        for act in state.queue:
            for target in self.targets:
                if target in act.targets:
                    for immuneact in self.args:
                        if isinstance(act, immuneact):
#                            print("%s is immune to %s" %(target, act))
                            state.resqueue.enqueue(act)
                        else:
                            newqueue.enqueue(act)
                else:
                    newqueue.enqueue(act)

        return newqueue

class Immuneelse(Action):
    name = "immuneelse"
    priority = 8

    def resolve(self, state):
        state.resolved(self)

        newqueue = Mqueue()
        for act in state.queue:
            for target in self.targets:
                if target in act.targets:
                    for immuneact in self.args:
                        if not isinstance(act, immuneact):
#                            print("%s is immune to %s" %(target, act))
                            state.resqueue.enqueue(act)
                        else:
                            newqueue.enqueue(act)
                else:
                    newqueue.enqueue(act)

        return newqueue

class Makehidden(Action):
    name = "makehidden"
    priority = 11

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            # all actions targeting a hidden player fail
            newqueue = Mqueue()
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
        for target in self.targets:
            newqueue = Mqueue()
            for act in state.queue:
                if killfound or (not (isinstance(act, Kill) and target in act.targets)):
                    newqueue.enqueue(act)
                else:
                    killfound = True
#                    print("kill %s canceled by protect" % act.targets)
                    state.resolved(act)
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
            if act.actor == source:
                newact = copy.deepcopy(act)
                newact.targets[0] = dest
#                print("newact:",newact)
                newqueue.enqueue(newact)
            else:
                newqueue.enqueue(act)
        return newqueue

class Reflex(Action):

    name = "reflex"
    priority = 9

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            for act in state.queue:
                if target in act.targets:
                    for reflexact in self.args:
                        reflexact.actor = target
                        reflexact.targets = [act.actor]
                        state.queue.enqueue(reflexact)

        return state.queue

class Track(Action):

    name = "track"
    priority = 90

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            bussed = state.bussedslot(target)
            acted = False
            targets = []
            for act in state.queue + state.resqueue:
                if not isinstance(act, Untrackable) and act.actor == bussed:
                    targets.extend(act.targets)

            msg = "%s targeted %s" % (state.playerbyslot(bussed).name, ", ".join([state.playerbyslot(x).name for x in state.fix(targets)]) )
            state.queue.enqueue(Message(self.actor, [self.actor], [msg]))

        return state.queue

class Watch(Action):

    name = "watch"
    priority = 90

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            bussed = state.bussedslot(target)
            acted = False
            for act in state.queue + state.resqueue:
                if not isinstance(act, Untrackable) and act.actor == bussed:
                    acted = True
                    break

            result = "used an ability" if acted else "didn't use an ability"

            msg = "%s %s" % (state.playerbyslot(bussed).name, result)

            state.queue.enqueue(Message(self.actor, [self.actor], [msg]))

        return state.queue

class Patrol(Action):

    name = "patrol"
    priority = 90

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            bussed = state.bussedslot(target)
            fakename = state.playerbyslot(target).name
            actors = []

            for act in state.queue + state.resqueue:
                if not isinstance(act, Patrol) and not isinstance(act, Untrackable) and bussed in state.fix(act.targets):
                    actors.append(act.actor)

            msg = "%s was targeted by %s" % (fakename, ", ".join([state.playerbyslot(x).name for x in actors]) )
            state.queue.enqueue(Message(self.actor, [self.actor], [msg]))

        return state.queue

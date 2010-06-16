from mafqueue import Mqueue

import copy

class Untrackable:
    pass

class Action:
    name = "none"
    priority = 99999999

    def __init__(self, actor, targets, args={}):
        self.actor = actor
        self.targets = targets
        self.args = args

    def __lt__(self, other):
        return self.__class__.priority < other.__class__.priority

    def __str__(self):
        return self.__class__.name
#        return("Action: %s %s %s" % (self.actor, self.__class__.name, self.targets))

    def resolve(self, state):
        return state.queue

class Message(Action, Untrackable):
    name = "message"
    priority = 100

    def resolve(self, state):
        if 'msg' in self.args:
            for slot in self.targets:
                msg = self.args['msg']
                state.messageslot(slot, msg)
                print("message from %s to %s: %s" % (self.actor, slot, msg))

        return state.queue

class Vote(Action, Untrackable):
    name = "vote"
    priority = 99

    def resolve(self, state):
        state.resolved(self)

        player = state.playerbyslot(self.actor)

        maxvotes = 1
        if 'maxvotes' in self.args:
            maxvotes = self.args['maxvotes']
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
            state.queue.enqueue(Message(self.actor, [self.actor], {'msg':msg}))

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
            if 'how' in self.args:
                how = self.args['how']
            state.message(None, "%s (%s) was %s"%(player.name, player.flip(), how))
            state.resetvotes()

        return state.queue

class SuperKill(Action):
    name = "superkill"
    priority = 70
    def resolve(self, state):
        return Kill.resolve(self, state)

class Lynch(Action):
    name = "lynch"
    priority = 70

    def resolve(self, state):
        self.args['how'] = 'lynched'
        state.votecount(True)
        return Kill.resolve(self, state)

class PoisonKill(Action):
    name = "poisonkill"
    priority = 70
    def resolve(self, state):
        self.args['how'] = 'poisoned'
        return Kill.resolve(self, state)

class Poison(Action):
    name = "poison"
    priority = 70

    def resolve(self, state):
        state.resolved(self)

        delayedact = PoisonKill(self.actor, self.targets)
        phases = self.args.get('phases', 2)
        state.delay(phases, delayedact)

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
                    phases = self.args.get('phases', 1)
                    state.delay(phases, delayedact)
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

class Eavesdrop(Action, Untrackable):
    name = "eavesdrop"
    priority = 95

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
            state.queue.enqueue(Message(self.actor, [target], {'msg':msg}))

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


# uses two keys in args:
# 'immune' a list of classes that this action will nullify
# 'not' reverse the comparison (immunity is susceptibility)

# immune means you're immune to the action(s) in the list
# example would be Godfather, which is immune to kills

# not immune means you're immune to everything except subclasses of the listed action
# an example would be Ascetic, which is immune to all actions except kills
class Immune(Action):
    name = "immune"
    priority = 8

    def resolve(self, state):
        state.resolved(self)

        immune = self.args.get('immune', [])
        if 'not' in self.args:
            operator = lambda x: not x
        else:
            operator = lambda x: x

        newqueue = Mqueue()
        for act in state.queue:
            for target in self.targets:
                if target in act.targets:

                    for immuneact in immune:
                        if operator(isinstance(act, immuneact)):
                            state.resqueue.enqueue(act)
                        else:
                            newqueue.enqueue(act)
                else:
                    newqueue.enqueue(act)

        return newqueue

    def __str__(self):
        msg = [self.__class__.name]
        if 'not' in self.args:
            msg.insert(0, 'not')
        if 'immune' in self.args:
            msg.append(self.args['immune'].name)
        return " ".join(msg)

class Reflex(Action):
    name = "reflex"
    priority = 9

    def resolve(self, state):
        state.resolved(self)

        for target in self.targets:
            for act in state.queue:
                if target in act.targets:
                    if 'action' in self.args:
                        reflexact = self.args['action']
                        newact = copy.deepcopy(reflexact)
                        newact.actor = target
                        if not newact.targets:
                            newact.targets = [act.actor]
                        state.queue.enqueue(newact)

        return state.queue

    def __str__(self):
        msg = [self.__class__.name]
        if 'action' in self.args:
            msg.append(self.args['action'].name)
        return " ".join(msg)

class Hide(Action):
    name = "hide"
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
            if act.actor == source:
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
            acted = False
            targets = []
            for act in state.queue + state.resqueue:
                if not isinstance(act, Untrackable) and act.actor == bussed:
                    targets.extend(act.targets)

            msg = "%s targeted %s" % (state.playerbyslot(bussed).name, ", ".join([state.playerbyslot(x).name for x in state.fix(targets)]) )
            state.queue.enqueue(Message(self.actor, [self.actor], {'msg':msg}))

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
                if not isinstance(act, Untrackable) and act.actor == bussed:
                    acted = True
                    break

            result = "used an ability" if acted else "didn't use an ability"

            msg = "%s %s" % (state.playerbyslot(bussed).name, result)

            state.queue.enqueue(Message(self.actor, [self.actor], {'msg':msg}))

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
                if not isinstance(act, Patrol) and not isinstance(act, Untrackable) and bussed in state.fix(act.targets):
                    actors.append(act.actor)

            msg = "%s was targeted by %s" % (fakename, ", ".join([state.playerbyslot(x).name for x in actors]) )
            state.queue.enqueue(Message(self.actor, [self.actor], {'msg':msg}))

        return state.queue

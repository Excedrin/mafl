from mafqueue import Mqueue
import faction
import sanity
from misc import Some
import copy

import ability
import phase

class ActionBase:
    name = "none"
    priority = 99999999

    notrack = False
    noimmune = False
    notrigger = False
    noblock = False
    nobus = False
    noredir = False

    def __init__(self, actor, targets, args={}, rename=None):
        self.actor = actor
        self.targets = targets
        self.args = copy.deepcopy(args)
        if rename:
            self.name = rename

        self.used = False
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

    notrack = True

    def resolve(self, state):
        if 'msg' in self.args:
            for slot in self.targets:
                msg = self.args['msg']
                state.messageslot(slot, msg)
                print("message from %s to %s: %s" % (self.actor, slot, msg))

        return state.queue

class PubMessage(Action):
    name = "pubmessage"
    priority = 100

    notrack = True

    def resolve(self, state):
        if 'msg' in self.args:
            msg = self.args['msg']
            state.message(None, msg)
            print("public message from %s: %s" % (self.actor, msg))

        return state.queue

# priority here matters, it has to resolve before auto actions
class Vote(Action):
    name = "vote"
    priority = 5

    notrack = True
    noimmune = True
    notrigger = True

    maxvotes = 1

    def resolve(self, state):
        self.used = True
        state.resolved(self)

        player = state.playerbyslot(self.actor)

        state.vote(self.actor, self.targets[0:self.maxvotes])

        return state.queue

class Voteop(Action):
    class Sub:
        op = lambda x,y: x - y
        verb = "lost"
    class Add:
        op = lambda x,y: x + y
        verb = "gained"

    Add.undo = Sub
    Sub.undo = Add

    # trade makes this either votesteal or votegive
    trade = False

    name = "voteblock"
#    name = "motivate"
    priority = 30

    op = Sub

    phases = 2
    undo = False

    def resolve(self, state):
        for slot in self.targets:
            if self.nobus:
                player = state.playerbyslot(slot)
            else:
                bus = self.args.get('bus', None)
                player = state.playerbyslotbus(slot, bus)

            for abi in player.allabilities():
                if issubclass(abi.action, Vote):
                    maxvotes = abi.args.get('maxvotes', abi.action.maxvotes)
                    abi.args['maxvotes'] = self.op.op(maxvotes, 1)
                    self.used = True

                    state.message(player.name, "You've %s a vote"%self.op.verb)

        state.resolved(self)

        if self.used and not self.undo:
            delayedact = Voteop(0, self.targets,
                                args={'op':self.op.undo, 'undo':True, 'notrack':True,
                                    'noimmune':True, 'notrigger':True,
                                    'noblock':True, 'bus':copy.copy(state.bus) })
            state.delay(self.phases, delayedact)

            if self.trade:
                print("found voteop w/trade")
                actor = state.playerbyslot(self.actor)
                for abi in actor.allabilities():
                    if issubclass(abi.action, Vote):
                        maxvotes = abi.args.get('maxvotes', abi.action.maxvotes)
                        abi.args['maxvotes'] = self.op.undo.op(maxvotes, 1)
                        state.message(actor.name, "You've %s a vote"%self.op.undo.verb)

                delayedact = Voteop(0, [self.actor],
                                    args={'op':self.op, 'undo':True, 'notrack':True,
                                        'noimmune':True, 'notrigger':True,
                                        'nobus':True, 'noblock':True,
                                        'bus':copy.copy(state.bus) })
                state.delay(self.phases, delayedact)

        return state.queue

class Alter(Action):
    name = "alter"
    priority = 19

    def resolve(self, state):
        for target in self.targets:
            for act in state.queue:
                if isinstance(act, Inspect) and target in act.targets:
                    if isinstance(act.inspect, sanity.Sane):
                        act.inspect = sanity.Insane(act.inspect.factions)
                    elif isinstance(act.inspect, sanity.Insane):
                        act.inspect = sanity.Sane(act.inspect.factions)
                    self.used = True

        state.resolved(self)
        return state.queue

class Inspect(Action):
    name = "inspect"
    priority = 20
    inspect = sanity.Sane([faction.Mafia, faction.Town])

    def resolve(self, state):
        for slot in self.targets:
            target = state.playerbyslotbus(slot)
            intended = state.playerbyslot(slot)

            msg = intended.name+" "+self.inspect.result(target)
            state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))
            self.used = True

        state.resolved(self)
        return state.queue

class Kill(Action):
    name = "kill"
    priority = 70
    how = "was killed"

    def resolve(self, state):
        for slot in self.targets:
            nobus = self.args.get('nobus', False)
            if nobus:
                player = state.playerbyslot(slot)
            else:
                player = state.playerbyslotbus(slot)
            if player.living:
                player.living = False
                print("kill resolved (%s killed by %s)" % (player.name, self.actor))
                msg = "%s %s"%(player.name, self.how)
                state.message(None, msg)
                state.resetvotes()
                state.enqueue(Flip(self.actor, [slot]))
                self.used = True
            else:
                print("kill resolved (%s already dead)" % (player.name))

        state.resolved(self)
        return state.queue

class SuperKill(Action):
    name = "superkill"
    priority = 70
    how = "was killed"

    noimmune = True

    def resolve(self, state):
        return Kill.resolve(self, state)

class Lynch(ActionBase):
    name = "lynch"
    priority = 70
    how = "was lynched"

    def resolve(self, state):
        state.votecount(True)
        return Kill.resolve(self, state)

class Suicide(Action):
    name = "suicide"
    priority = 70
    how = "comitted suicide"

    noimmune = True
    notrigger = True
    noblock = True

    def resolve(self, state):
        return Kill.resolve(self, state)

# resolve earlier than hide
class PoisonKill(Action):
    name = "poisonkill"
    priority = 10
    how = "was poisoned"

#    notrigger = True

    def resolve(self, state):
        return Kill.resolve(self, state)

class Poison(Action):
    name = "poison"
    priority = 70
    phases = 2

    notrigger = True

    def resolve(self, state):
        self.used = True
        state.resolved(self)

        bus = self.args.get('bus', None)
        player = state.playerbyslotbus(slot, bus)

        delayedact = PoisonKill(0, self.targets)
        state.delay(self.phases, delayedact,
                                args={'notrack':True, 'noimmune':True,
                                    'notrigger':True, 'noblock':True,
                                    'bus':copy.copy(state.bus) })
        return state.queue

class Flip(Action):
    name = "flip"
    priority = 74

    def resolve(self, state):
        for slot in self.targets:
            player = state.playerbyslot(slot)
            if not player.living:
                msg = "%s was a %s"%(player.name, player.flip())
                state.message(None, msg)
                self.used = True

        state.resolved(self)
        return state.queue

class FakeFlip(Action):
    name = "fakeflip"
    priority = 73

    def resolve(self, state):
        newqueue = Mqueue()
        for act in state.queue:
            for slot in self.targets:
                if isinstance(act, Flip) and slot in act.targets:
                    player = state.playerbyslot(slot)
                    if not player.living:
                        faction = self.args.get('faction', player.faction)
                        role = self.args.get('role', player.truename)
                        msg = "%s was a %s %s"%(player.name, faction.name, role)
                        state.message(None, msg)
                        self.used = True
                else:
                    newqueue.enqueue(act)

        state.resolved(self)
        return newqueue

class Resurrect(Action):
    name = "resurrect"
    priority = 72
    how = "returned to life"

    def resolve(self, state):
        for slot in self.targets:
            player = state.playerbyslotbus(slot)
            if not player.living:
                player.living = True
                msg = "%s %s"%(player.name, self.how)
                state.message(None, msg)
                self.used = True

        state.resolved(self)

        return state.queue

class Recruit(Action):
    name = "recruit"
    priority = 75
    msg = 'recruited'

    def resolve(self, state):
        actor = state.playerbyslot(self.actor)

        if actor.living:
            for slot in self.targets:
                player = state.playerbyslotbus(slot)
                if 'role' in self.args:
                    player.setrole(self.args['role'])
                dorecruit = False
                if 'okalign' in self.args:
                    for okalign in self.args['okalign']:
                        if isinstance(player.faction, okalign):
                            dorecruit = True
                else: # no restriction, so recruit anyone
                    dorecruit = True

                if dorecruit:
                    player.faction = actor.faction

                    msg = "%s %s"%(self.msg, player.name)
                    state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))

                    state.message(player.name, player.fullrolepm(state))
                    state.resetvotes()
                    self.used = True

        state.resolved(self)

        return state.queue

class Copy(Action):
    name = "copy"
    priority = 10

    def resolve(self, state):
        if len(self.targets) == 2:
            source = self.targets[0]
            dest = self.targets[1]
#            print("copy src: %s dst: %s" %(source,dest))

            newqueue = Mqueue()
            for act in state.queue:
                if act.actor == source:
                    newact = copy.deepcopy(act)
                    newact.actor = source
                    newact.targets[0] = dest
#                    print("newact:",newact)
                    newqueue.enqueue(newact)
                    self.used = True
                newqueue.enqueue(act)

            state.resolved(self)
        else:
            print(self.name + " requires 2 targets")
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
        if len(self.targets) == 2:
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

            state.resolved(self)
#        print("state.bus",state.bus)
        else:
            print(self.name + " requires 2 targets")

        return state.queue

class Delay(Action):
    name = "delay"
    priority = 13

    phases = 1

    def resolve(self, state):
        newqueue = Mqueue()
        for act in state.queue:
            if act.actor in [state.bussedslot(x) for x in self.targets]:
                if act.args.get('delayed', False):
                    newqueue.enqueue(act)
                else:
                    delayedact = copy.deepcopy(act)
                    delayedact.args['delayed'] = True
                    state.delay(self.phases, delayedact)
                    self.used = True
            else:
                newqueue.enqueue(act)

        state.resolved(self)
        return newqueue

class Block(Action):
    name = "block"
    priority = 14
    superblock = False

    def resolve(self, state):
        newqueue = Mqueue()

        for act in state.queue:
            if not act.noblock and not act.actor in self.targets:
                newqueue.enqueue(act)
                self.used = True
            # blocked actions don't go into resqueue

        state.resolved(self)
        return newqueue

class Eavesdrop(Action):
    name = "eavesdrop"
    priority = 95
    notrack = True

    def resolve(self, state):
        newqueue = Mqueue()
        for act in state.queue:
            for target in self.targets:
                if isinstance(act, Message) and target in act.targets:
                    newact = copy.deepcopy(act)
                    newact.targets = [self.actor]
                    newqueue.enqueue(newact)
                    self.used = True
            newqueue.enqueue(act)
        state.resolved(self)
        return newqueue

class Friend(Action):
    name = "friend"
    priority = 20

    def resolve(self, state):
        actor = state.playerbyslot(self.actor)

        msg = "%s is %s" % (actor.name, actor.faction.name)
        for target in state.fix(self.targets):
            state.enqueue(Message(self.actor, [target], {'msg':msg}))
            self.used = True

        state.resolved(self)
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

    guard = Both

    def resolve(self, state):
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

        self.used = killfound
        state.resolved(self)
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
                            self.used = True
                        else:
                            newqueue.enqueue(act)
                else:
                    newqueue.enqueue(act)

        state.resolved(self)
        return newqueue

    def __str__(self):
        msg = [self.getname()]
        if 'not' in self.args:
            msg.insert(0, 'not')
        msg.append(", ".join([x.name for x in self.immune]))
        return " ".join(msg)

class Disable(Action):
    name = "disable"
    priority = 7
    superblock = True
    phases = 2
    def resolve(self, state):
        delayedact = Block(0, self.targets, args={'super':True})
        state.delay(self.phases, delayedact)

        return Block.resolve(self, state)

class Reflex(Action):
    name = "reflex"
    priority = 8
    triggers = [Action]
    action = None

    notrigger = True
    noimmune = True

    resolvers = []

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
                            newact.targets = []

                            print("reflex resolvers",self.resolvers)
                            for resolver in self.resolvers:
                                print("calling resolver gettargets")
                                newact.targets.extend(resolver.gettargets(state, self.actor, act.actor, []))
                            if not newact.targets:
                                newact.targets = [act.actor]
                            print("newact targets:",newact.targets,state.names(newact.targets))
                            newacts.append(newact)

        resolved = False
        for newact in newacts:
            state.enqueue(newact)
            resolved = True

        if resolved:
            self.used = resolved
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
        newqueue = Mqueue()
        for target in self.targets:
            # all actions targeting a hidden player fail
            for act in state.queue:
                if act.targets[0] != target:
                    newqueue.enqueue(act)
                    self.used = True
        state.resolved(self)
        return newqueue

class ReverseProtect(Action):
    name = "reverseprotect"
    priority = 45

    def resolve(self, state):
        protectfound = False
        newqueue = Mqueue()

        for target in self.targets:
            for act in state.queue:
                if protectfound or (not (isinstance(act, Protect)
                                    and target in act.targets)):
                    newqueue.enqueue(act)
                else:
                    print("reverseprotect found protect, enqueuing kill")
                    newqueue.enqueue(Kill(self.actor, act.targets))
                    protectfound = True
                    state.resolved(act)

        self.used = protectfound
        state.resolved(self)
        return newqueue

class Protect(Action):
    name = "protect"
    priority = 50

    def resolve(self, state):
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

        self.used = killfound
        state.resolved(self)
        return newqueue

class Antidote(Action):
    name = "antidote"
    priority = 50

    def resolve(self, state):
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

        self.used = killfound
        state.resolved(self)
        return newqueue

class Redirect(Action):
    name = "redirect"
    priority = 15

    def resolve(self, state):
        if len(self.targets) == 2:
            source = self.targets[0]
            dest = self.targets[1]

            newqueue = Mqueue()
            for act in state.queue:
                # don't redirect self targeted actions
                if act.actor == source and not act.noredir and act.targets[0] != act.actor:
                    newact = copy.deepcopy(act)
                    newact.targets[0] = dest
                    #print("newact:",newact)
                    newqueue.enqueue(newact)
                    self.used = True
                else:
                    newqueue.enqueue(act)
            state.resolved(self)
        else:
            print(self.name + " requires 2 targets")
        return newqueue

class Track(Action):
    name = "track"
    priority = 90

    def resolve(self, state):
        for target in self.targets:
            bussed = state.bussedslot(target)
            targets = []
            for act in state.queue + state.resqueue:
                if not act.notrack and act.actor == bussed:
                    targets.extend(act.targets)

            if targets:
                res = ", ".join([state.playerbyslot(x).name for x in state.fix(targets)]) 
            else:
                res = "nobody"
            msg = "%s targeted %s" % (state.playerbyslot(bussed).name, res)
            state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))
            self.used = True

        state.resolved(self)
        return state.queue

class Watch(Track):
    name = "watch"
    priority = 90

    def resolve(self, state):
        for target in self.targets:
            bussed = state.bussedslot(target)
            acted = False
            for act in state.queue + state.resqueue:
                if not act.notrack and act.actor == bussed:
                    acted = True
                    break

            result = "used an ability" if acted else "didn't use an ability"

            msg = "%s %s" % (state.playerbyslot(bussed).name, result)

            state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))
            self.used = True

        state.resolved(self)
        return state.queue

class Patrol(Track):
    name = "patrol"
    priority = 90

    def resolve(self, state):
        for target in self.targets:
            bussed = state.bussedslot(target)
            fakename = state.playerbyslot(target).name
            actors = []

            for act in state.queue + state.resqueue:
                if not isinstance(act, Patrol) and not act.notrack and bussed in state.fix(act.targets):
                    actors.append(act.actor)

            if actors:
                res = ", ".join([state.playerbyslot(x).name for x in actors])
            else:
                res = "nobody"

            msg = "%s was targeted by %s" % (fakename, res)

            state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))
            self.used = True

        state.resolved(self)
        return state.queue

class Steal(Action):
    name = "steal"
    priority = 41

    def resolve(self, state):
        for target in state.fix(self.targets):
            player = state.playerbyslot(target)
            abis = list(filter(lambda x:not x.auto and not x.nosteal, 
                        player.abilities.values()))

            if abis:
                abi = state.rng.choice(abis)
                actor = state.playerbyslot(self.actor)
                player.removeability(abi)
                actor.addability(abi)
                self.used = True
                msg = "stole %s" %(abi)
                state.enqueue(Message(self.actor, [self.actor], {'msg':msg}))
            
        state.resolved(self)
        return state.queue

class Swap(Action):
    name = "swap"
    priority = 42

    def resolve(self, state):
        if len(self.targets) == 2:
            p1 = state.playerbyslot(self.targets[0])
            p2 = state.playerbyslot(self.targets[1])
            print("swap %s %s <-> %s %s"%(p1.name, p1.role, p2.name, p2.role))

            p1.role, p2.role = p2.role, p1.role
            p1.truename, p2.truename = p2.truename, p1.truename
            p1.abilities, p2.abilities = p2.abilities, p1.abilities

            state.message(p1.name, p1.fullrolepm(state))
            state.message(p2.name, p2.fullrolepm(state))
            state.resolved(self)
        else:
            print(self.name + " requires 2 targets")

        return state.queue

class Morph(Action):
    name = "morph"
    priority = 43

    def resolve(self, state):
        if len(self.targets) == 1:
            p1 = state.playerbyslot(self.actor)
            p2 = state.playerbyslot(self.targets[0])
            print("morph %s %s -> %s %s"%(p1.name, p1.role, p2.name, p2.role))

            p1.role = p2.role
            p1.truename = p2.truename
            p1.clearabilities()
            for abi in p2.allabilities():
                p1.addability(abi)
            p1.addability(ability.Ability(FakeFlip, phase.Any, auto=True, resolvers=[ability.Ability.Self()], args={'faction':p2.faction} ))

            state.message(p1.name, p1.fullrolepm(state))
            state.resolved(self)
        else:
            print(self.name + " requires 2 targets")

        return state.queue

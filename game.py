import traceback
from difflib import SequenceMatcher

import copy

import time
import timers

import mafl

class Game:
    def __init__(self, rng):
        self.channel = None

        self.queue = mafl.Mqueue()
        self.resqueue = mafl.Mqueue()
        self.autoqueue = mafl.Mqueue()
        self.delayqueue = mafl.Mqueue()

        self.bus = {}

        self.slot = {}
        self.name = {}

        self.players = []

        self.out = []

        self.phase = mafl.phase.Idle
        self.newphase = mafl.phase.Idle

        self.votes = {}

        self.timers = timers.Timers()
        self.lastvc = 0

        self.fake = {}

        self.rng = rng

    def message(self, who, message):
        if who in self.fake:
            self.out.append((self.fake[who], "(%s) %s"%(who, message)))
        else:
            self.out.append((who, message))
####
    def slotbyname(self, name):
        if name in self.slot:
            return self.slot[name]
        else:
#            print("no slot",name)
            return None

    def slotbyplayer(self, player):
        return self.slotbyname(player.name)

    def playerbyslot(self, slot):
        return self.players[slot]

    def bussedslot(self, slot):
        if slot in self.bus:
            return rng.choice(self.bus[slot])
        else:
            return slot

    def playerbyslotbus(self, slot):
        if slot in self.bus:
            busedslot = rng.choice(self.bus[slot])
            return self.playerbyslot(busedslot)
        else:
            return self.playerbyslot(slot)

    def playerbyname(self, name):
        slot = self.slotbyname(name)
        if slot is None:
            print("no player",name)
            return None
        else:
            return self.playerbyslot(slot)

    def messageslot(self, slot, message):
        target = self.playerbyslot(slot)
        if target.living:
            self.message(target.name, message)
####
    def fix(self, targets):
        return [self.bussedslot(x) for x in targets]

    def nextphase(self, newphase=None):
        if newphase:
            self.newphase = newphase
        else:
            self.newphase = self.phase.nextphase

    def newplayer(self, name):
        slot = len(self.players)
        self.slot[name] = slot
        self.name[slot] = name
        self.players.append(mafl.Player(name))

    def join(self, name):
        if self.phase == mafl.phase.Idle or self.phase == mafl.phase.Signups:
            self.newplayer(name)

    def enqueue(self, action):
        print("enqueue",action)
        self.queue.enqueue(action)

    def resolved(self, action):
        self.resqueue.enqueue(action)

    def resolve(self, verbose=False):
        if self.queue:
            self.queue.merge(self.autoqueue)
            if verbose:
                print("resolve")
            while self.queue:
                if verbose:
                    print("resolve q:", self.queue)
                act = self.queue.pop()
                if verbose:
                    print("resolve act:", act)
                self.queue = act.resolve(self)
            if verbose:
                print("resolve done")

    def resetresolved(self):
        self.resqueue = mafl.Mqueue()

    def resetvotes(self):
        self.votes = {}

    def resetuses(self):
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            for abi in player.allabilities():
                abi.reset()

    def resetout(self):
        self.out = []

    def resetphase(self):
        self.resetuses()
        self.resetout()
        self.resetvotes()

        self.queue = Mqueue()
        self.resqueue = Mqueue()
        self.autoqueue = Mqueue()

        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            player.living = True

        self.bus = {}

    def reset(self):
        channel = self.channel
        self.__init__(self.rng)
        self.channel = channel

    def playernames(self):
        return list(self.name.values())

    def names(self, slots):
        return [self.name[x] for x in slots]

    def livingslots(self):
        living = []
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            if player.living:
                living.append(slot)
        return living

    def living(self):
        living = []
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            if player.living:
                living.append(player)
        return living

    def dead(self):
        dead = []
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            if not player.living:
                dead.append(player)
        return dead

    def checkwin(self):
        winners = []
        losers = []
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            if player.faction.win(self, player):
                winners.append(slot)
            else:
                losers.append(slot)
        if not self.living():
            return ((), (), list(self.slot.keys()))
        if winners:
            return (winners, losers, ())
        return ((), (), ())


    def start(self, channel):
        if self.phase == mafl.phase.Idle:
            print("start")
            self.channel = channel

            self.nextphase()

            self.timers.settimer('start', 307)

    def wait(self):
        if self.phase == mafl.phase.Signups:
            if self.timers.remaining('start') < 61:
                self.timers.settimer('start', 61)
                self.message(None, "game start delayed %d seconds"%61)

    def go(self, now):
        if self.phase == mafl.phase.Signups:
            if now == "now":
                self.nextphase()
            else:
                if self.timers.remaining('start') > 11:
                    self.timers.settimer('start', 11)

    def tick(self):
        if self.phase == mafl.phase.Signups:
            remaining = self.timers.remaining('start')
            if remaining < 0:
                self.nextphase()
            elif remaining in (307,229,97,31,7):
                self.timers.dec('start')
                self.message(None, "game starts in %d seconds"%(remaining))

        if self.phase == mafl.phase.Day:
            self.timers.setfirst('vote', 181)
            if self.timers.expired('vote'):
                self.votecount()
                self.timers.settimer('vote', 181)

        if self.phase == mafl.phase.Night:
            self.timers.setfirst('night', 181)
            remaining = self.timers.remaining('night')
            if remaining in (173,89,37,11):
                self.timers.dec('night')
                self.message(None, "night ends in %d seconds"%(remaining))
            if remaining < 0:
                self.message(None, "night timed out")
                self.nextphase()

            if self.timers.expired('randomize'):
                self.nextphase()

    def phasemsg(self, who=None):
        self.message(who, self.phase.name)

    def livingmsg(self, who=None):
        living = self.living()
        msg = "%d living players: %s"% (len(living), ", ".join([x.name for x in living]))
        self.message(who, msg)

    def fullrolepm(self, name):
        player = self.playerbyname(name)
        if player:
            self.message(name, player.fullrolepm(self))

    def done(self, name):
        player = self.playerbyname(name)
        if player:
            player.done(self)
            self.message(name, 'OK')

    def delay(self, phases, action):
        self.delayqueue.enqueue((phases - 1, action))
        
    def undelay(self):
        newqueue = mafl.Mqueue()
        while self.delayqueue:
            (phases, action) = self.delayqueue.pop()
            print("undelay:",phases)
            if phases <= 0:
                self.queue.enqueue(action)
            else:
                newqueue.enqueue((phases - 1, action))

        self.delayqueue = newqueue

    def useautoabilities(self):
        for player in self.players:
            slot = self.slotbyplayer(player)
            abilities = player.allabilities()
            for action in filter(None, map(lambda x: x.useauto(self, self.phase, slot), abilities)):
                print("enqueue(auto)",action)
                self.autoqueue.enqueue(action)

    def run(self):
        done = 0
#        print("state.run")

        if self.phase.started:
            # if nobody has an unused ability, end the phase
            # if no player has an ability (night or day) then
            # it'll instantly alternate between day and night forever
            unused = False
            for name, slot in self.slot.items():
                player = self.playerbyslot(slot)
                if player.unused(self):
                    unused = True
            if not unused:
                # anti-meta timer (range is maybe too small)
                self.timers.setfirst('randomize', self.rng.randint(3,13))

            if self.phase.instant:
                self.resolve()

            win,lose,draw = self.checkwin()
            if win or draw:
                if draw:
                    self.message(None, "game over, draw: %s"% ", ".join(self.names(draw)))
                else:
                    self.message(None, "game over, winners: %s"% ", ".join(self.names(win)))
                    self.message(None, "losers: %s"% ", ".join(self.names(lose)))
                self.nextphase(mafl.phase.Done)

        # phase changed!
        if self.phase != self.newphase:
            # reset timers
            if self.phase != mafl.phase.Idle:
                self.timers = timers.Timers()

            if self.phase == mafl.phase.Signups:
                self.setup = mafl.setup.Setup(self.rng, self.players)
                if self.setup.setroles():
                    print("sending roles")
                    # send role pms
                    for name, slot in self.slot.items():
                        player = self.playerbyslot(slot)
                        self.message(name, player.fullrolepm(self))
                else:
                    self.message("Failed to assign roles")
                    self.reset()

            self.undelay()

            # resolve the previous phase's actions,
            # must do this before enqueuing auto abilities
            self.resolve()

            self.phase = self.newphase
            if self.phase != mafl.phase.Done:
                self.phasemsg()
                self.livingmsg()

            self.resetresolved()
            self.resetuses()
            self.resetvotes()

            self.useautoabilities()

        ret = copy.deepcopy(self.out)

        if self.phase is mafl.phase.Done:
            self.reset()

        self.out = []

        return ret

    def majority(self):
        return int(len(self.living()) / 2)

    def vote(self, voter, targets):
        print("vote",voter,targets)
        # unvote first
        for k,v in self.votes.items():
            if voter in self.votes[k]:
                self.votes[k].remove(voter)
        for k in list(self.votes.keys()):
            if not self.votes[k]:
                del self.votes[k]

        lynched = False
        for target in targets:
            if target in self.votes and self.votes[target]:
                self.votes[target].append(voter)
            else:
                self.votes[target] = [voter]

            if len(self.votes[target]) > self.majority():
                self.enqueue(mafl.actions.Lynch(voter, [target]))
                lynched = True
        if lynched:
            self.nextphase()

    def votecount(self, force=False):
        if force or time.time() > self.lastvc + 10:
            self.lastvc = time.time()

            self.message(None, "Vote count: %d to lynch"%(self.majority()+1))
            for k,v in self.votes.items():
                voters = [self.playerbyslot(x).name for x in self.votes[k]]
                wagon = "%s (%d) - %s" % (self.playerbyslot(k).name, len(voters), ', '.join(voters))
                self.message(None, wagon)

    def replace(self, p1, p2):
        slot = self.slotbyname(p1)
        if slot != None:
            player = self.playerbyslot(slot)
            player.name = p2
            self.slot[p2] = slot
            del self.slot[p1]
            self.name[slot] = p2

            if p1 in self.fake:
                self.fake[p2] = self.fake[p1]
            self.message(None, "replaced %s with %s"%(p1,p2))
        else:
            self.message(None, "didn't find player %s"%p1)

    def setrole(self, p1, rolename, add=False):
        newrole = mafl.role.roles.get(rolename, None)
        player = self.playerbyname(p1)
        if newrole and player:
            if add:
                player.addrole(newrole)
            else:
                player.setrole(newrole)
            self.message(None, "%s role set"%p1)
            return True
        elif not player:
            self.message(None, "didn't find player %s"%p1)
            return False
        elif not newrole:
            self.message(None, "didn't find role %s"%rolename)
            return False

    def showsetup(self, who):
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            self.message(who, name + ": " + player.fullrolepm(self))

    def fuzzy(self, tryname):
        best = 0
        match = None
        names = self.playernames()
        if tryname in names:
            return (tryname, 1, tryname)
        
        for name in filter(lambda x:len(x) > 1, names):
            ratio = SequenceMatcher(None, tryname.lower(), name.lower()).ratio()
            if ratio > best:
                best = ratio
                match = name
        return (tryname, best, match)

    def cleanargs(self, args):
        return [self.fuzzy(x) for x in args]

    def tryability(self, who, public, ability, args):
        player = self.playerbyname(who)
        if player:
            print("found player:",who,player)
            try:
                cleaned = []
                mangled = []
                for tryname, best, match in self.cleanargs(args):
                    if best > 0.6:
                        print("fuzzy match",tryname,best,match)
                        cleaned.append(match)
                    else:
                        mangled.append(tryname)

                if mangled:
                    self.message(who, "%s not found" %mangled)
                else:
                    if player.faction and ability in player.faction.abilities:
                        (res, msg) = player.faction.abilities[ability].use(self, public, player, cleaned)
                        # faction ability failed, now try player ability
                        if not res and ability in player.abilities:
                            (res, msg) = player.abilities[ability].use(self, public, player, cleaned)
                        self.message(who, msg)
                    elif ability in player.abilities:
                        (res, msg) = player.abilities[ability].use(self, public, player, cleaned)
                        self.message(who, msg)

            except Exception as e:
                print("exception trying to handle player ability: %s\n%s\n" %(ability, e))
                traceback.print_exc()

    def newsetup(self):
        self.phase = mafl.phase.Signups
        self.nextphase()

    def testsetup(self, args):  
        if len(args) >= 1 and int(args[0]):
            n = int(args[0])
            print("testsetup for ",n)

            fakeplayers = [mafl.Player(x) for x in range(n)]
            self.setup = mafl.setup.Setup(self.rng, fakeplayers)
            if self.setup.setroles():
                byfac = {}
                for p in fakeplayers:
                    if p.faction.name in byfac:
                        byfac[p.faction.name].append(p.truename)
                    else:
                        byfac[p.faction.name] = [p.truename]
                msg = []
                for k,v in byfac.items():
                    msg.append("%s: %s" %(k, ", ".join(v)))
                self.message(None, "; ".join(msg))

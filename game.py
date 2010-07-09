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
        self.delayqueue = mafl.Mqueue()

        self.bus = {}

        self.slot = {} # name to slot
        self.name = {} # slot to name

        self.players = []

        self.out = []

        self.phase = mafl.phase.Idle
        self.newphase = mafl.phase.Idle

        self.votes = {}

        self.timers = timers.Timers()
        self.lastvc = 0

        self.fake = {}

        self.rng = rng
        self.verbose = False

    def message(self, who, message):
        if who in self.fake:
            self.out.append((self.fake[who], "(%s) %s"%(who, message)))
        else:
            self.out.append((who, message))
####
    def slotbyname(self, name):
        return self.slot.get(name.lower(), None)

    def slotbyplayer(self, player):
        return self.slotbyname(player.name.lower())

    def playerbyslot(self, slot):
        return self.players[slot]

    def bussedslot(self, slot, bus=None):
        if bus:
            zuh = bus.get(slot, [slot])
        else:    
            zuh = self.bus.get(slot, [slot])
        print("in bussed slot",zuh)
        return self.rng.choice(zuh)

    def playerbyslotbus(self, slot, bus=None):
        return self.playerbyslot(self.bussedslot(slot, bus))

    def playerbyname(self, name):
        slot = self.slotbyname(name.lower())
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
        print("nextphase",newphase)
        if newphase:
            self.newphase = newphase
        else:
            self.newphase = self.phase.nextphase

    def newplayer(self, name, virtual=False):
        if not self.playerbyname(name):
            slot = len(self.players)
            self.slot[name.lower()] = slot
            self.name[slot] = name
            self.players.append(mafl.Player(name, virtual))

    def join(self, channel, name):
        if name != "nolynch" and self.playerbyname(name) is None:
            if self.phase == mafl.phase.Idle:
                self.start(channel)
                self.newplayer(name)
            elif self.phase == mafl.phase.Signups:
                self.newplayer(name)

    def enqueue(self, action):
        print("enqueue",action)
        self.queue.enqueue(action)

    def resolved(self, action):
        self.resqueue.enqueue(action)

    def delay(self, phases, action):
        print("delay",phases,action)
        self.delayqueue.enqueue((phases - 1, action))
        
    def resolve(self):
        if self.queue:
            if self.verbose:
                print("resolve",self.queue)
            self.useautoabilities()
            count = len(self.queue) + 10
            if self.verbose:
                print("resolve",count)
            while self.queue and count > 0:
                count -= 1
                if self.verbose:
                    print("resolve q:", self.queue)
                act = self.queue.pop()
                if self.verbose:
                    print("resolve act:", act)
                self.queue = act.resolve(self)
            if self.verbose:
                print("resolve done",count)

    def resetresolved(self):
        self.resqueue = mafl.Mqueue()

    def resetqueues(self):
        self.resqueue = mafl.Mqueue()
        self.queue = mafl.Mqueue()

    def resetvotes(self):
        self.votes = {}

    def resetuses(self):
        for player in self.realplayers():
            for abi in player.allabilities():
                abi.reset()

    def resetout(self):
        self.out = []

    def startphase(self):
        print("startphase")
        self.resetuses()
        self.resetqueues()
        self.resetvotes()
#        self.useautoabilities()

        if self.phase == mafl.phase.Signups:
            self.message(None, "New game starting, join now")

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
            if player.living and not player.virtual:
                living.append(slot)
        return living

    def realplayers(self):
        return list(filter(lambda x: not x.virtual, self.players))

    def living(self):
        living = []
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            if player.living and not player.virtual:
                living.append(player)
        return living

    def dead(self):
        dead = []
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            if not player.living and not player.virtual:
                dead.append(player)
        return dead

    def checkwin(self):
        winners = []
        losers = []
        draw = []
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            if not player.virtual:
                if player.faction.win(self, player):
                    winners.append(slot)
                else:
                    losers.append(slot)
                draw.append(slot)
        if not self.living():
            return ((), (), draw)
        if winners:
            return (winners, losers, ())
        return ((), (), ())

    def start(self, channel):
        if self.phase == mafl.phase.Idle:
            print("start")

            self.newplayer('nolynch', True)

            self.channel = channel
            self.nextphase()
            self.timers.settimer('start', 307)

    def wait(self):
        if self.phase == mafl.phase.Signups:
            remaining = self.timers.remaining('start')
            if remaining and remaining < 61:
                self.timers.settimer('start', 61)
                self.message(None, "game start delayed %d seconds"%61)

    def go(self, now):
        if self.phase == mafl.phase.Signups:
            if now == "now":
                self.nextphase()
            else:
                remaining = self.timers.remaining('start')
                if remaining and remaining.v > 11:
                    self.timers.settimer('start', 11)

    def tick(self):
        if self.phase == mafl.phase.Signups:
            remaining = self.timers.remaining('start')
            if remaining and remaining.v < 0:
                self.nextphase()
            elif remaining and remaining.v in (307,229,97,31,7):
                self.timers.dec('start')
                self.message(None, "game starts in %d seconds"%(remaining.v))

        if self.phase == mafl.phase.Day:
            self.timers.setfirst('vote', 181)
            if self.timers.expired('vote'):
                self.votecount()
                self.timers.settimer('vote', 181)

        if self.phase == mafl.phase.Night:
            self.timers.setfirst('night', 181)
            remaining = self.timers.remaining('night')
            if remaining and remaining.v in (173,89,37,11):
                self.timers.dec('night')
                self.message(None, "night ends in %d seconds"%(remaining.v))
            if remaining and remaining.v < 0:
                self.message(None, "night timed out")
                self.nextphase()

            if self.timers.expired('randomize'):
                self.nextphase()

        if self.phase.started:
            for p in self.living():
                self.timers.setfirst('%' + p.name.lower(), 307)
                remaining = self.timers.remaining('%' + p.name.lower())
 
                if remaining and remaining.v in (23,5):
                    self.message(p.name, "modkill in %d seconds"%remaining.v)
                    self.timers.dec('%' + p.name.lower())
                if remaining and remaining.v <= 0:
                    target = self.slotbyname(p.name)

                    self.enqueue(mafl.actions.Disable(0, [target]))
                    self.enqueue(mafl.actions.SuperKill(0, [target], args={'how':'died of boredom'}))

    def phasemsg(self, who=None):
        self.message(who, self.phase.name)

    def deadmsg(self, who=None):
        dead = self.dead()
        msg = "%d dead players: %s"% (len(dead), ", ".join([x.name for x in dead]))
        self.message(who, msg)

    def livingmsg(self, who=None):
        living = self.living()
        msg = "%d living players: %s"% (len(living), ", ".join([x.name for x in living]))
        self.message(who, msg)

    def fullrolepm(self, name):
        player = self.playerbyname(name)
        if player and not player.virtual:
            self.message(name, player.fullrolepm(self))

    def done(self, name):
        player = self.playerbyname(name)
        if player and not player.virtual:
            player.done(self)
            self.message(name, 'OK')

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

    def useautoability(self, player):
        slot = self.slotbyplayer(player)
        abilities = player.allabilities()
        for action in filter(None, map(lambda x: x.useauto(self, self.phase, slot), abilities)):
            print("enqueue(auto)",action)
            self.enqueue(action)

    def useautoabilities(self):
        for player in self.players:
            self.useautoability(player)

    def run(self):
        done = 0
#        print("state.run")

        if self.phase.started:
            # if nobody has an unused ability, end the phase
            # if no player has an ability (night or day) then
            # it'll instantly alternate between day and night forever

            # check for unused actions
            unused = False
            for name, slot in self.slot.items():
                player = self.playerbyslot(slot)
                if player.unused(self):
                    unused = True
            if not unused:
                # anti-meta timer (range is maybe too small)
                self.timers.setfirst('randomize', self.rng.randint(3,13))
                # tick will cause nextphase

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
                self.showsetuppost(None)

        # phase changed!
        if self.phase != self.newphase:
            # reset timers
            if self.phase != mafl.phase.Idle:
                self.timers = timers.Timers()

            if self.phase == mafl.phase.Signups:
                pl = self.realplayers()
                self.setup = mafl.setup.Setup(self.rng)
           
                if self.setup.getroles(len(pl)):
                    self.setup.setroles(pl)
                    print("sending roles")
                    # send role pms
                    for name, slot in self.slot.items():
                        player = self.playerbyslot(slot)
                        if not player.virtual:
                            self.message(name, player.fullrolepm(self))
                else:
                    self.message(None, "Failed to assign roles, canceled game")
                    self.nextphase(mafl.phase.Done)

            self.undelay()

            # resolve the previous phase's actions,
            # must do this before enqueuing auto abilities
            self.resolve()

            self.phase = self.newphase
            if self.phase.started:
                self.phasemsg()
                self.livingmsg()

            self.startphase()

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
                print("votecount:",k,v)
                voters = [self.playerbyslot(x).name for x in v]
                wagon = "%s (%d) - %s" % (self.playerbyslot(k).name, len(voters), ', '.join(voters))
                self.message(None, wagon)

    def replace(self, p1, p2, quiet=False):
        if p1 == p2:
            return

        slot = self.slotbyname(p1)
        slot2 = self.slotbyname(p2)
        if slot != None and slot2 == None:

            player = self.playerbyslot(slot)
            if player.virtual:
                return
            player.name = p2
            self.slot[p2.lower()] = slot
            del self.slot[p1.lower()]
            self.name[slot] = p2

            if p1 in self.fake:
                self.fake[p2] = self.fake[p1]
            self.timers.remove('%'+p1.lower())
            self.timers.settimer('%'+p2.lower(), 307)
            res = "replaced %s with %s"%(p1,p2)
        elif slot2:
            res = "player %s is already playing"%p2
        else:
            res =  "player %s doesn't exist"%p1

        if not quiet:
            self.message(None, res)

    def setrole(self, who, args):
        align = "town"
        add = False
        if len(args) >= 2:
            p1 = args[0]
            rolename = args[1]
        if len(args) == 3:
            align = args[2]
        if len(args) == 4:
            add = args[3] == '+'

        player = self.playerbyname(p1)
        newrole = mafl.role.roles.get(rolename, None)
        faction = mafl.faction.factions.get(align, None)

        facinstance = None
        if faction:
            for p in self.players:
                if isinstance(p.faction, faction):
                    facinstance = p.faction
                    break
            if not facinstance:
                facinstance = faction()
        else:
            facinstance = player.faction

        if newrole and player and facinstance:
            if add:
                player.addrole(newrole)
            else:
                player.setrole(newrole, facinstance)

            self.useautoability(player)

            self.message(None, "%s role set"%p1)
            return True
        elif not player:
            self.message(None, "didn't find player %s"%p1)
            return False
        elif not newrole:
            self.message(None, "didn't find role %s"%rolename)
            return False
        elif not faction:
            self.message(None, "didn't find faction %s"%align)

    def showsetup(self, who):
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            if not player.virtual:
                self.message(who, name + ": " + player.fullrolepm(self))

    def showsetuppost(self, who):
        byfac = {}
        for p in self.realplayers():
            if str(p.faction) in byfac:
                byfac[str(p.faction)].append(p.name+" was a "+p.truename)
            else:
                byfac[str(p.faction)] = [p.name+" was a "+p.truename]
        msg = []
        for k,v in byfac.items():
            msg.append("%s: %s" %(k, ", ".join(v)))
        self.message(who, "setup: " + "; ".join(msg))

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
            self.timers.settimer(who.lower(), 307)

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

            self.setup = mafl.setup.Setup(self.rng)
            if self.setup.getroles(n):
                byfac = {}
                for r,f in self.setup.roles:
                    if str(f.name) in byfac:
                        byfac[str(f.name)].append(r.getname())
                    else:
                        byfac[str(f.name)] = [r.getname()]
                msg = []
                for k,v in byfac.items():
                    msg.append("%s: %s" %(k, ", ".join(v)))
                return "; ".join(msg)

    def gotest(self, to, who, args):
        if len(args) >= 1 and int(args[0]) <= 26 and self.phase == mafl.phase.Idle:
            self.verbose = True
            self.start(to)
            n = int(args[0])
            print("runtest for ",n)
            for name in [chr(ord('a') + x) for x in range(n)]:
                self.newplayer(name)
                self.fake[name] = who
            self.phase = mafl.phase.Signups
            self.nextphase(mafl.phase.Day)

    def makefake(self, who, args):
        fakecmd = args[1]
        if fakecmd[0] == '%':
            fakecmd = fakecmd[1:]
        if fakecmd == 'join':
            self.fake[args[0]] = who

    def rolepower(self, who, args):
        if len(args) == 3:
            rolename = args[0]
            n = int(args[1])
            align = args[2]
            if n > 26:
                return

            faction = mafl.faction.factions.get(align, None)
            r = mafl.role.roles.get(rolename, None)
            if r and faction:
                power = r.power(n, faction)
                self.message(who, "%s %0.2f" %(r.getname(), power))

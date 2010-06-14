import time
import copy
import random

import mafl

class State:
    def __init__(self):
        self.channel = None

        self.queue = mafl.Mqueue()
        self.resqueue = mafl.Mqueue()
        self.bus = {}

        self.slot = {}
        self.name = {}

        self.players = []

        self.out = []

        self.phase = mafl.phase.Idle
        self.newphase = mafl.phase.Idle

        self.votes = {}

        self.timers = {}

    def message(self, who, message):
        self.out.append((who, message))
####
    def slotbyname(self, name):
        if name in self.slot:
            return self.slot[name]
        else:
            print("no slot",name)
            return None

    def slotbyplayer(self, player):
        return self.slotbyname(player.name)

    def playerbyslot(self, slot):
        return self.players[slot]

    def bussedslot(self, slot):
        if slot in self.bus:
            return random.choice(self.bus[slot])
        else:
            return slot

    def playerbyslotbus(self, slot):
        if slot in self.bus:
            busedslot = random.choice(self.bus[slot])
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

    def newplayer(self, name, faction):
        slot = len(self.players)
        self.slot[name] = slot
        self.name[slot] = name
        self.players.append(mafl.Player(name, faction))

    def enqueue(self, action):
        print("enqueue",action)
        self.queue.enqueue(action)

    def resolved(self, action):
        self.resqueue.enqueue(action)

    def resolve(self):
#        print("resolve")
        while self.queue:
#            print("resolve q:", self.queue)
            act = self.queue.pop()
#            print("resolve act:", act)
            self.queue = act.resolve(self)
#        print("resolve done")

    def resetvotes(self):
        self.votes = {}

    def resetuses(self):
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            for abi in player.allabilities():
                abi.used = False

    def resetout(self):
        self.out = []

    def resetphase(self):
        self.resetuses()
        self.resetout()
        self.resetvotes()

        self.queue = Mqueue()
        self.resqueue = Mqueue()

        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            player.living = True
        self.bus = {}

    def reset(self):
        channel = self.channel
        self.__init__()
        self.channel = channel

    def playernames(self):
        return list(self.name.values())

    def names(self, slots):
        return [self.name[x] for x in slots]

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

    def setup(self):
        self.resetout()

        town = mafl.faction.Town()
        maf = mafl.faction.Mafia()
        survivor = mafl.faction.Survivor()

        tmp = list(self.players)
        random.shuffle(tmp)
        if len(tmp) == 3:
            p = tmp.pop()
            p.faction = maf
            mafl.role.Townie().setrole(p)
            for p in tmp:
                p.faction = town
                mafl.role.Townie().setrole(p)
            self.message(None, "game started")
            self.nextphase()
        elif len(tmp) == 4:
            p = tmp.pop()
            p.faction = maf
            mafl.role.Townie().setrole(p)

            if random.choice([True,False]): # 50/50 a doctor
                p = tmp.pop()
                p.faction = town
                mafl.role.Doctor().setrole(p)

            for p in tmp:
                p.faction = town
                mafl.role.Townie().setrole(p)

            self.message(None, "game started")
            self.nextphase()
        elif len(tmp) == 5:
            p = tmp.pop()
            p.faction = maf
            mafl.role.Townie().setrole(p)

            if random.choice([True,False]):
                p = tmp.pop()
                p.faction = town
                mafl.role.Doctor().setrole(p)

            for p in tmp:
                p.faction = town
                mafl.role.Townie().setrole(p)
            self.message(None, "game started")
            self.nextphase()
        elif len(tmp) == 6:
            p = tmp.pop()
            p.faction = maf
            p = tmp.pop()
            p.faction = maf

            if random.choice([True,False]):
                p = tmp.pop()
                p.faction = town
                mafl.role.Doctor().setrole(p)
            else:
                p = tmp.pop()
                p.faction = town
                mafl.role.Cop().setrole(p)

            for p in tmp:
                p.faction = town
            self.message(None, "game started")
            self.nextphase()
        elif len(tmp) == 7:
            p = tmp.pop()
            p.faction = maf
            p = tmp.pop()
            p.faction = maf

            if random.choice([True,False]):
                p = tmp.pop()
                p.faction = town
                mafl.role.Doctor().setrole(p)

            if random.choice([True,False]):
                p = tmp.pop()
                p.faction = town
                mafl.role.Cop().setrole(p)

            for p in tmp:
                p.faction = town
    
            self.message(None, "game started")
            self.nextphase()
        else:
            self.message(None, "needs more players")

    def start(self, channel):
        if self.phase == mafl.phase.Idle:
            print("start")
            self.channel = channel

            self.nextphase()

            self.timers['start'] = time.time() + 20

    def tick(self):
        if self.phase == mafl.phase.Signups:
            timer = self.timers['start']
            if time.time() > timer:
                self.nextphase()
                self.setup()
            elif time.time() + 60 > timer:
                remaining = int(timer - time.time())
                if remaining > 0 and remaining % 10 == 0:
                    self.message(None, "game starts in %d seconds"%(remaining))

    def livingmsg(self):
        msg = "living players: %s"% ", ".join([x.name for x in self.living()])
        self.message(None, msg)

    def rolepm(self, name):
        player = self.playerbyname(name)
        self.message(name, player.rolepm(self))

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
#                print("state.run, found no unused actions")
                self.nextphase()

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

        if self.phase != self.newphase:
            if self.phase == mafl.phase.Signups:
                print("sending roles", self.phase, self.newphase)
                # send role pms
                for name, slot in self.slot.items():
                    player = self.playerbyslot(slot)
                    self.message(name, player.rolepm(self))

            self.resolve()
            self.message(None, self.newphase.name)
            self.livingmsg()

            self.resetuses()
            self.resetvotes()

            self.phase = self.newphase

        ret = copy.deepcopy(self.out)

        if self.phase is mafl.phase.Done:
            self.reset()

        self.out = []

        return ret

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

            if len(self.votes[target]) > int(len(self.living()) / 2):
                self.enqueue(mafl.actions.Lynch(voter, [target]))
                lynched = True
        if lynched:
            self.nextphase()

    def votecount(self):
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
            self.message(None, "replaced %s with %s"%(p1,p2))
        else:
            self.message(None, "didn't find %s"%p1)

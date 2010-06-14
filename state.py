from mafqueue import *
from player import *
import random

import mafia
import faction
import phase
import role

class State:
    def __init__(self):
        self.channel = None

        self.queue = Mqueue()
        self.resqueue = Mqueue()
        self.bus = {}

        self.slot = {}
        self.names = {}

        self.players = []

        self.out = []

        self.phase = phase.Starting
        self.newphase = phase.Starting

        self.votes = {}

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
        self.names[slot] = name
        self.players.append(Player(name, faction))

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

    def resetuses(self):
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            for _, abi in player.abilities.items():
                abi.used = False
            for _, abi in player.faction.abilities.items():
                abi.used = False

    def resetout(self):
        self.out = []

    def reset(self):
        self.queue = Mqueue()
        self.resqueue = Mqueue()
        for name, slot in self.slot.items():
            player = self.playerbyslot(slot)
            player.living = True
        self.bus = {}

        self.phase = phase.Starting
        self.newphase = phase.Starting

    def playernames(self):
        return list(self.names.values())

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
        self.channel = channel

        self.resetout()

        town = faction.town()
        maf = faction.mafia()
        survivor = faction.survivor()

        tmp = list(self.players)
        random.shuffle(tmp)
        if len(tmp) == 3:
            p = tmp.pop()
            p.faction = maf
            role.Townie().setrole(p)
            for p in tmp:
                p.faction = town
                role.Townie().setrole(p)
            self.message(None, "game started")
            self.nextphase()
        elif len(tmp) == 4:
            p = tmp.pop()
            p.faction = maf
            role.Townie().setrole(p)

            if random.choice([True,False]): # 50/50 a doctor
                p = tmp.pop()
                p.faction = town
                role.Doctor().setrole(p)

            for p in tmp:
                p.faction = town
                role.Townie().setrole(p)

            self.message(None, "game started")
            self.nextphase()
        elif len(tmp) == 5:
            p = tmp.pop()
            p.faction = maf
            role.Townie().setrole(p)

            if random.choice([True,False]):
                p = tmp.pop()
                p.faction = town
                role.Doctor().setrole(p)

            for p in tmp:
                p.faction = town
                role.Townie().setrole(p)
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
                role.Doctor().setrole(p)
            else:
                p = tmp.pop()
                p.faction = town
                role.Cop().setrole(p)

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
                role.Doctor().setrole(p)

            if random.choice([True,False]):
                p = tmp.pop()
                p.faction = town
                role.Cop().setrole(p)

            for p in tmp:
                p.faction = town
            self.message(None, "game started")
            self.nextphase()
        else:
            self.message(None, "needs more players")

    def livingmsg(self):
        msg = "living players: %s"% ", ".join([x.name for x in self.living()])
        self.message(None, msg)

    def run(self):
        done = 0
#        print("state.run")

        if self.phase != phase.Starting:

            # if nobody has an unused ability, end the phase
            # if no player has an ability (night or day) then
            # it'll instantly alternate between day and night forever
            unused = False
            for name, slot in self.slot.items():
                player = self.playerbyslot(slot)
                for _,ability in player.faction.abilities.items():
                    if ability.phase is self.phase and not ability.used:
                        unused = True
#                        print("state.run, unused action", ability.action)
                for _,ability in player.abilities.items():
                    if ability.phase is self.phase and not ability.used:
                        unused = True
#                        print("state.run, unused action", ability.action)
            if not unused:
#                print("state.run, found no unused actions")
                self.nextphase()

            if self.phase.instant:
                self.resolve()

            win,lose,draw = self.checkwin()
            if win or draw:
                if draw:
                    self.message(None, "game over, draw: %s"% draw)
                else:
                    self.message(None, "game over, winners: %s"% win)
                    self.message(None, "losers: %s"% lose)
                self.reset()

        if self.phase != self.newphase:
            self.resolve()
            self.message(None, self.newphase.name)
            self.livingmsg()

            self.resetuses()

            self.phase = self.newphase

        ret = list(self.out)
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
                self.enqueue(mafia.actions.Kill(voter, [target], ["lynched"]))
                lynched = True
        if lynched:
            self.nextphase()

    def votecount(self):
        for k,v in self.votes.items():
            voters = [self.playerbyslot(x).name for x in self.votes[k]]
            wagon = "%s (%d) - %s" % (self.playerbyslot(k).name, len(voters), ', '.join(voters))
            self.message(None, wagon)

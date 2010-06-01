from queue import *
from player import *
from random import choice

class State:
    def __init__(self):
        self.players = {}
        self.queue = Queue()
        self.resqueue = Queue()
        self.bus = {}

    def newplayer(self, player):
        self.players[player] = Player(player)

    def enqueue(self, action):
        self.queue.enqueue(action)

    def resolved(self, action):
        self.resqueue.enqueue(action)

    def resolve(self):
        print("resolve")
        while self.queue:
            print("resolve q:", self.queue)
            act = self.queue.pop()
            print("resolve act:", act)
            self.queue = act.resolve(self)
        print("resolve done")

    def reset(self):
        self.queue = Queue()
        self.resqueue = Queue()
        for name,player in self.players.items():
            player.living = True
        self.bus = {}

    def living(self):
        living = []
        for name,player in self.players.items():
            if player.living:
                living.append(player)
        return living

    def dead(self):
        dead = []
        for name,player in self.players.items():
            if not player.living:
                dead.append(player)
        return dead

    def lookup(self, player):
        if player in self.bus:
            return self.players[choice(self.bus[player])]
        else:
            return self.players[player]

    def fix(self, targets):
        return map(lambda x: self.lookup(x).name, targets)

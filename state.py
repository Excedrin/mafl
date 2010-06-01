from queue import *
from player import *

class State:
    def __init__(self):
        self.players = {}
        self.queue = Queue()
        self.resqueue = Queue()

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
            player.bussed = None

    def living(self):
        living = []
        dead = []
        for name,player in self.players.items():
            if player.living:
                living.append(player.name)
            else:
                dead.append(player.name)
        print("living: %s" % living)
        print("dead: %s" % dead)

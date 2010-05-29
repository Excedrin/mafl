from queue import *
from player import *

class State:
    def __init__(self):
        self.players = {}
        self.queue = Queue()

    def newplayer(self, player):
        self.players[player] = Player(player)

    def enqueue(self, action):
        self.queue.enqueue(action)

    def resolve(self):
        print("resolve")
        while self.queue:
            print("resolve q:", self.queue)
            act = self.queue.pop()
            print("resolve act:", act)
            self.queue = act.resolve(self)
        print("resolve done")


    def reset(self):
        for name,player in self.players.items():
            player.living = True
            player.targets = []

    def target(self, actor, targets):
        self.players[actor].targets.extend(targets)
    
    def gettargets(self, actor):
        return self.players[actor].targets

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

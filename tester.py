#!/usr/bin/python3

import random
import game

import mafl
from mafl import actions

def results(g):
    g.resolve()
    print("living:", [x.name for x in g.living()])
    print("dead:", [x.name for x in g.dead()])

    win,lose,draw = g.checkwin()
    if win or draw:
        if draw:
            print("game over, draw:", draw)
        else:
            print("game over, winners:", win)
            print("losers:", lose)

    print()
    g.reset()

def setup():
    g = game.Game(random.Random())
#    g.verbose = True
    a = g.newplayer("Alice")
    a.setrole(mafl.role.RoleBase, maf)
    b = g.newplayer("Bob")
    b.setrole(mafl.role.RoleBase, town)
    c = g.newplayer("Carol")
    c.setrole(mafl.role.RoleBase, town)
    d = g.newplayer("Dave")
    d.setrole(mafl.role.RoleBase, survivor)

    return g,a,b,c,d

def enqueue(state, action, player, targets, args={}):
    targetslots = [state.slotbyplayer(x) for x in targets]
#    print("targetslots",targetslots)
    state.enqueue(action(state.slotbyplayer(player), targetslots, args))

town = mafl.faction.Town()
maf = mafl.faction.Mafia()
survivor = mafl.faction.Survivor()

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Kill, Alice, [Bob])
enqueue(g, actions.Inspect, Bob, [Alice])
enqueue(g, actions.Eavesdrop, Carol, [Bob])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Protect, Carol, [Alice])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Inspect, Alice, [Bob])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Copy, Dave, [Bob, Bob])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Inspect, Alice, [Bob])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Protect, Carol, [Alice])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Hide, Bob, [Bob])
enqueue(g, actions.Redirect, Carol, [Alice, Alice])
enqueue(g, actions.Inspect, Alice, [Bob])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Copy, Dave, [Alice, Alice])
enqueue(g, actions.Friend, Dave, [Carol])
enqueue(g, actions.Block, Dave, [Carol])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Block, Alice, [Bob])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Watch, Carol, [Alice,Bob])
enqueue(g, actions.Track, Dave, [Carol])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Track, Alice, [Bob])
enqueue(g, actions.Track, Bob, [Alice])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Protect, Dave, [Carol])
enqueue(g, actions.Kill, Bob, [Carol])
enqueue(g, actions.Track, Alice, [Bob,Dave])
enqueue(g, actions.Patrol, Carol, [Carol])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Protect, Dave, [Carol])
enqueue(g, actions.Kill, Bob, [Carol])
enqueue(g, actions.Kill, Bob, [Carol])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Guard, Dave, [Carol])
enqueue(g, actions.Kill, Bob, [Carol])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Reflex, Dave, [Dave], {'action':actions.Kill(Dave, [], args={'nobus': True})} )
enqueue(g, actions.Inspect, Bob, [Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Immune, Dave, [Dave], {'immune':[actions.Kill]} )
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Immune, Dave, [Dave], {'not':0, 'immune':[actions.Kill]} )
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
enqueue(g, actions.Kill, Bob, [Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Bus, Alice, [Dave, Carol])
#enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
#enqueue(g, actions.Kill, Bob, [Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Bus, Alice, [Dave, Carol])
enqueue(g, actions.Inspect, Carol, [Dave])
enqueue(g, actions.Kill, Bob, [Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Bus, Alice, [Dave, Carol])
enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
enqueue(g, actions.Kill, Bob, [Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Guard, Carol, [Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Protect, Carol, [Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Protect, Carol, [Bob])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Bus, Alice, [Alice, Dave])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Patrol, Carol, [Alice])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Bus, Alice, [Dave, Bob])
#enqueue(g, actions.Watch, Carol, [Bob])
#enqueue(g, actions.Track, Carol, [Bob])
enqueue(g, actions.Patrol, Carol, [Dave])
enqueue(g, actions.Inspect, Dave, [Bob])
results(g)

## win condition test

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Kill, Bob, [Alice])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Kill, Bob, [Carol,Dave])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Kill, Alice, [Bob,Carol])
results(g)

g, Alice, Bob, Carol, Dave = setup()
enqueue(g, actions.Kill, Alice, [Bob])
enqueue(g, actions.Guard, Carol, [Bob])
results(g)

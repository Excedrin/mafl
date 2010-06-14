#!/usr/bin/python3
import mafia
from mafia import actions

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

town = mafia.faction.town()
maf = mafia.faction.mafia()
survivor = mafia.faction.survivor()

g = mafia.State()
g.newplayer("Alice", maf)
g.newplayer("Bob", town)
g.newplayer("Carol", town)
g.newplayer("Dave", survivor)

Alice = g.playerbyname("Alice")
Bob = g.playerbyname("Bob")
Carol = g.playerbyname("Carol")
Dave = g.playerbyname("Dave")

def enqueue(state, action, player, targets, args=[]):
    targetslots = [state.slotbyplayer(x) for x in targets]
#    print("targetslots",targetslots)
    state.enqueue(action(state.slotbyplayer(player), targetslots, args))

enqueue(g, actions.Kill, Alice, [Bob])
enqueue(g, actions.Inspect, Bob, [Alice])
enqueue(g, actions.Eavesdrop, Carol, [Bob])
results(g)

enqueue(g, actions.Protect, Carol, [Alice])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Inspect, Alice, [Bob])
results(g)

enqueue(g, actions.Copy, Dave, [Bob, Bob])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Inspect, Alice, [Bob])
results(g)

enqueue(g, actions.Protect, Carol, [Alice])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Makehidden, Bob, [Bob])
enqueue(g, actions.Redirect, Carol, [Alice, Alice])
enqueue(g, actions.Inspect, Alice, [Bob])
results(g)

enqueue(g, actions.Copy, Dave, [Alice, Alice])
enqueue(g, actions.Friend, Dave, [Carol])
enqueue(g, actions.Block, Dave, [Carol])
results(g)

enqueue(g, actions.Block, Alice, [Bob])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Watch, Carol, [Alice,Bob])
enqueue(g, actions.Track, Dave, [Carol])
results(g)

enqueue(g, actions.Track, Alice, [Bob])
enqueue(g, actions.Track, Bob, [Alice])
results(g)

enqueue(g, actions.Protect, Dave, [Carol])
enqueue(g, actions.Kill, Bob, [Carol])
enqueue(g, actions.Track, Alice, [Bob,Dave])
enqueue(g, actions.Patrol, Carol, [Carol])
results(g)

enqueue(g, actions.Protect, Dave, [Carol])
enqueue(g, actions.Kill, Bob, [Carol])
enqueue(g, actions.Kill, Bob, [Carol])
results(g)

enqueue(g, actions.Guard, Dave, [Carol])
enqueue(g, actions.Kill, Bob, [Carol])
results(g)

enqueue(g, actions.Reflex, Dave, [Dave], [actions.Kill(Dave, [])] )
enqueue(g, actions.Inspect, Bob, [Dave])
results(g)

enqueue(g, actions.Immune, Dave, [Dave], [actions.Kill] )
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
results(g)

enqueue(g, actions.Immuneelse, Dave, [Dave], [actions.Kill] )
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
results(g)

enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
enqueue(g, actions.Kill, Bob, [Dave])
results(g)

enqueue(g, actions.Bus, Alice, [Dave, Carol])
#enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
#enqueue(g, actions.Kill, Bob, [Dave])
results(g)

enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Bus, Alice, [Dave, Carol])
enqueue(g, actions.Inspect, Carol, [Dave])
enqueue(g, actions.Kill, Bob, [Dave])
results(g)

enqueue(g, actions.Bus, Alice, [Dave, Carol])
enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Inspect, Carol, [Dave])
enqueue(g, actions.Kill, Bob, [Dave])
results(g)

enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Guard, Carol, [Dave])
results(g)

enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Protect, Carol, [Dave])
results(g)

enqueue(g, actions.Bus, Alice, [Bob, Dave])
enqueue(g, actions.Kill, Bob, [Dave])
enqueue(g, actions.Protect, Carol, [Bob])
results(g)

enqueue(g, actions.Bus, Alice, [Alice, Dave])
enqueue(g, actions.Kill, Bob, [Alice])
enqueue(g, actions.Patrol, Carol, [Alice])
results(g)

enqueue(g, actions.Bus, Alice, [Dave, Bob])
#enqueue(g, actions.Watch, Carol, [Bob])
#enqueue(g, actions.Track, Carol, [Bob])
enqueue(g, actions.Patrol, Carol, [Dave])
enqueue(g, actions.Inspect, Dave, [Bob])
results(g)

## win condition test

enqueue(g, actions.Kill, Bob, [Alice])
g.resolve()

results(g)

enqueue(g, actions.Kill, Bob, [Carol,Dave])
g.resolve()

results(g)

enqueue(g, actions.Kill, Alice, [Bob,Carol])
g.resolve()

results(g)

enqueue(g, actions.Kill, Alice, [Bob])
enqueue(g, actions.Guard, Carol, [Bob])
g.resolve()
results(g)

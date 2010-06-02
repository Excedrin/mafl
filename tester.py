#!/usr/bin/python3
import mafia

def results(g):
    g.resolve()
    print("living:", list(map(lambda x: x.name, g.living())))
    print("dead:", list(map(lambda x: x.name, g.dead())))

    win,lose,draw = g.checkwin()
    if win or draw:
        if draw:
            print("game over, draw:", draw)
        else:
            print("game over, winners:", win)
            print("losers:", lose)

    print()
    g.reset()

g = mafia.State()
g.newplayer("a")
g.newplayer("b")
g.newplayer("c")
g.newplayer("d")

town = mafia.Ftown()
maf = mafia.Fmaf()
survivor = mafia.Fsurvivor()
g.players["a"].faction = maf
g.players["b"].faction = town
g.players["c"].faction = town
g.players["d"].faction = survivor

g.enqueue(mafia.actkill("a", ["b"]))
g.enqueue(mafia.actinspect("b", ["a"]))
g.enqueue(mafia.acteavesdrop("c", ["b"]))
results(g)

g.enqueue(mafia.actprotect("c", ["a"]))
g.enqueue(mafia.actkill("b", ["a"]))
g.enqueue(mafia.actinspect("a", ["b"]))
results(g)

g.enqueue(mafia.actcopy("d", ["b", "b"]))
g.enqueue(mafia.actkill("b", ["a"]))
g.enqueue(mafia.actinspect("a", ["b"]))
results(g)

g.enqueue(mafia.actprotect("c", ["a"]))
g.enqueue(mafia.actkill("b", ["a"]))
g.enqueue(mafia.actmakehidden("b", ["b"]))
g.enqueue(mafia.actredirect("c", ["a", "a"]))
g.enqueue(mafia.actinspect("a", ["b"]))
results(g)

g.enqueue(mafia.actcopy("d", ["a", "a"]))
g.enqueue(mafia.actfriend("d", ["c"]))
g.enqueue(mafia.actblock("d", ["c"]))
results(g)

g.enqueue(mafia.actblock("a", ["b"]))
g.enqueue(mafia.actkill("b", ["a"]))
g.enqueue(mafia.actwatch("c", ["a","b"]))
g.enqueue(mafia.acttrack("d", ["c"]))
results(g)

g.enqueue(mafia.acttrack("a", ["b"]))
g.enqueue(mafia.acttrack("b", ["a"]))
results(g)

g.enqueue(mafia.actprotect("d", ["c"]))
g.enqueue(mafia.actkill("b", ["c"]))
g.enqueue(mafia.acttrack("a", ["b","d"]))
g.enqueue(mafia.actpatrol("c", ["c"]))
results(g)

g.enqueue(mafia.actprotect("d", ["c"]))
g.enqueue(mafia.actkill("b", ["c"]))
g.enqueue(mafia.actkill("b", ["c"]))
results(g)

g.enqueue(mafia.actguard("d", ["c"]))
g.enqueue(mafia.actkill("b", ["c"]))
results(g)

g.enqueue(mafia.actreflex("d", ["d"], [mafia.actkill("d", [])] ))
g.enqueue(mafia.actinspect("b", ["d"]))
results(g)

g.enqueue(mafia.actimmune("d", ["d"], [mafia.actkill] ))
g.enqueue(mafia.actkill("b", ["d"]))
g.enqueue(mafia.actinspect("c", ["d"]))
results(g)

g.enqueue(mafia.actimmuneelse("d", ["d"], [mafia.actkill] ))
g.enqueue(mafia.actkill("b", ["d"]))
g.enqueue(mafia.actinspect("c", ["d"]))
results(g)

g.enqueue(mafia.actbus("a", ["b", "d"]))
g.enqueue(mafia.actinspect("c", ["d"]))
g.enqueue(mafia.actkill("b", ["d"]))
results(g)

g.enqueue(mafia.actbus("a", ["d", "c"]))
#g.enqueue(mafia.actbus("a", ["b", "d"]))
g.enqueue(mafia.actinspect("c", ["d"]))
#g.enqueue(mafia.actkill("b", ["d"]))
results(g)

g.enqueue(mafia.actbus("a", ["b", "d"]))
g.enqueue(mafia.actbus("a", ["d", "c"]))
g.enqueue(mafia.actinspect("c", ["d"]))
g.enqueue(mafia.actkill("b", ["d"]))
results(g)

g.enqueue(mafia.actbus("a", ["d", "c"]))
g.enqueue(mafia.actbus("a", ["b", "d"]))
g.enqueue(mafia.actinspect("c", ["d"]))
g.enqueue(mafia.actkill("b", ["d"]))
results(g)

g.enqueue(mafia.actbus("a", ["b", "d"]))
g.enqueue(mafia.actkill("b", ["d"]))
g.enqueue(mafia.actguard("c", ["d"]))
results(g)

g.enqueue(mafia.actbus("a", ["b", "d"]))
g.enqueue(mafia.actkill("b", ["d"]))
g.enqueue(mafia.actprotect("c", ["d"]))
results(g)

g.enqueue(mafia.actbus("a", ["b", "d"]))
g.enqueue(mafia.actkill("b", ["d"]))
g.enqueue(mafia.actprotect("c", ["b"]))
results(g)

g.enqueue(mafia.actbus("a", ["a", "d"]))
g.enqueue(mafia.actkill("b", ["a"]))
g.enqueue(mafia.actpatrol("c", ["a"]))
results(g)

g.enqueue(mafia.actbus("a", ["d", "b"]))
#g.enqueue(mafia.actwatch("c", ["b"]))
#g.enqueue(mafia.acttrack("c", ["b"]))
g.enqueue(mafia.actpatrol("c", ["d"]))
g.enqueue(mafia.actinspect("d", ["c"]))
results(g)

## win condition test

g.enqueue(mafia.actkill("b", ["a"]))
g.resolve()

results(g)

g.enqueue(mafia.actkill("b", ["c","d"]))
g.resolve()

results(g)

g.enqueue(mafia.actkill("a", ["b","c"]))
g.resolve()

results(g)

g.enqueue(mafia.actkill("a", ["b"]))
g.enqueue(mafia.actguard("c", ["b"]))
g.resolve()
results(g)

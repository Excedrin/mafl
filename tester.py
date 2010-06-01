#!/usr/bin/python3
import mafia

def results(g):
    g.resolve()
    print("living:",g.living())
    print("dead:",g.dead())
    print()
    g.reset()

g = mafia.State()
g.newplayer("a")
g.newplayer("b")
g.newplayer("c")
g.newplayer("d")

g.players["a"].align = "a"
g.players["b"].align = "b"
g.players["c"].align = "c"
g.players["d"].align = "d"

g.enqueue(mafia.actinspect("a", ["b"]))
results(g)

g.enqueue(mafia.actkill("b", ["a"]))
g.enqueue(mafia.actinspect("a", ["b"]))
results(g)

g.enqueue(mafia.actprotect("c", ["a"]))
g.enqueue(mafia.actkill("b", ["a"]))
g.enqueue(mafia.actinspect("a", ["b"]))
results(g)

g.enqueue(mafia.actprotect("c", ["a"]))
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

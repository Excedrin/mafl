#!/usr/bin/python3
import mafia

#['Action', 'Player', 'Queue', 'QueueIter', 'State', '__builtins__', '__doc__', '__file__', '__name__', '__package__', 'actcopy', 'actinspect', 'actkill', 'actmakehidden', 'actmessage', 'actprotect', 'copy', 'heapq']
#>>>

def results(g):
    g.resolve()
    g.living()
    print()
    g.reset()

g = mafia.State()
g.newplayer("a")
g.newplayer("b")
g.newplayer("c")
g.newplayer("d")

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

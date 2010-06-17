import random

import game
import dumper

rng = random.Random()

def rungame(bot, public, to, who, state):
    channel = state.channel
    if not channel and public:
        channel = to

    result = state.run()
    for target, l in result:
        print("res:",target,l)
        if target:
            bot.notice(target, l)
        elif channel:
            bot.privmsg(channel, l)
        else:
            bot.notice(who, l)

def tick(bot):
    state = bot.get('maf')
    if state:
        state.tick()
        rungame(bot, True, None, None, state)
    bot.store('maf', state)

def run(bot, command, to, who, args):
    if not command:
        return

    public = to and to[0] == "#"

    # in public, cmdchar is necessary
    if public:
        if command[0] == '%':
            command = command[1:]
        else:
            return
    else:
        # in private, cmdchar is optional
        if command[0] == '%':
            command = command[1:]

    state = bot.get('maf')

    if command == "reset":
        state = None

    if state == None:
        state = game.Game(rng)

    if command == "join":
        state.join(who)

    elif command == "done":
        state.done(who)

    elif command == "role":
        state.fullrolepm(who)

# mod commands
    elif command == "force":
        if len(args) >= 2:
            run(bot, args[1], to, args[0], args[2:])
        if args[1] == 'join' or args[1][1:] == 'join':
            state.fake[args[0]] = who

    elif command == "forcenextphase":
        state.nextphase()

    elif command == "replace":
        if len(args) == 2:
            state.replace(args[0], args[1])

    elif command == "setrole":
        if len(args) == 2:
            state.setrole(args[0], args[1])

    elif command == "dump":
        dumper.max_depth = 9
        print(dumper.dump(state))

# public informational commands
    elif public and command == "living":
        state.livingmsg()
    elif public and command == "votes":
        state.votecount()
    elif public and command == "phase":
        state.phasemsg()
    elif public and command == "start":
        state.start(to)
    elif public and command == "wait":
        state.wait()
    elif public and command == "go":
        state.go(args[0] if args else None)

# role commands
    elif command:
        print("game command %s args %s"%(command,args))
        state.tryability(who, public, command, args)

    rungame(bot, public, to, who, state)

    bot.store('maf', state)

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
        elif public:
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
    state = bot.get('maf')

    public = to and to[0] == "#"

    if command == "%reset":
        state = None

    if state == None:
        state = game.Game(rng)

    if command == "%join":
        state.join(who)

    elif command == "%done":
        state.done(who)

    elif command == "%setrole":
        if len(args) == 2:
            state.setrole(args[0], args[1])

    elif command == "%role":
        state.rolepm(who)

    elif command == "%force":
        if len(args) >= 2:
            run(bot, args[1], to, args[0], args[2:])
        if args[1] == '%join':
            state.fake[args[0]] = who

    elif command == "%living":
        state.livingmsg()

    elif command == "%forcenextphase":
        state.nextphase()

    elif command == "%phase":
        bot.reply(to, who, "%s" %state.phase.name)

    elif command == "%votes":
        state.votecount()

    elif command == "%replace":
        if len(args) == 2:
            state.replace(args[0], args[1])

    elif public and command == "%start":
        state.start(to)
    elif public and command == "%wait":
        state.wait()
    elif public and command == "%go":
        state.go(args[0] if args else None)

    elif command == "%dump":
        dumper.max_depth = 9
        print(dumper.dump(state))

    elif command and ((command[0] == '%') or not public):
        ability = command[1:] if command[0] == '%' else command
        print("args:",args)
        state.tryability(who, public, ability, args)

    rungame(bot, public, to, who, state)

    bot.store('maf', state)

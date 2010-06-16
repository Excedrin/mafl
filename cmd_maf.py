import game
import dumper

def rungame(bot, to, who, state):
    result = state.run()
    for target, l in result:
        print("res:",target,l)
        if target:
            bot.privmsg(target, l)
        elif state.channel:
            bot.privmsg(state.channel, l)
        else:
            bot.reply(to, who, l)

def tick(bot):
    state = bot.get('maf')
    if state:
        state.tick()
        rungame(bot, state.channel, state.channel, state)
    bot.store('maf', state)

def run(bot, command, to, who, args):
    state = bot.get('maf')

    if command == "%reset":
        state = None

    if state == None:
        state = game.Game()

    if command == "%join":
        state.join(who)

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

    elif to and to[0] == "#" and command == "%start":
        state.start(to)
    elif to and to[0] == "#" and command == "%wait":
        state.wait()
    elif to and to[0] == "#" and command == "%go":
        state.go(args[0] if args else None)

    elif command == "%dump":
        dumper.max_depth = 9
        print(dumper.dump(state))

    elif command and (command[0] == '%') or (to and to[0] != "#"):
        ability = command[1:]
        print("args:",args)
        state.tryability(who, ability, args)

    rungame(bot, to, who, state)

    bot.store('maf', state)

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

    if command == "help":
        bot.reply("normal commands: %s" % ", ".join(["join","start","go","wait",
                "done","role","testsetup","living","votes","phase","replace"]))
        bot.reply("mod commands: %s" % ", ".join(["reset","newsetup","force","forcep",
                "forcenextphase","showsetup","setrole"]))

    elif command == "join":
        state.join(who)

    elif command == "done":
        state.done(who)

    elif command == "role":
        state.fullrolepm(who)

# mod commands
    elif public and command == "newsetup":
        state.newsetup()
    elif public and command == "force":
        if len(args) >= 2:
            run(bot, args[1], to, args[0], args[2:])
        if args[1] == 'join' or args[1][1:] == 'join':
            state.fake[args[0]] = who

    elif public and command == "forcep":
        if len(args) >= 2:
            run(bot, args[1], "bot", args[0], args[2:])
        if args[1] == 'join' or args[1][1:] == 'join':
            state.fake[args[0]] = who

    elif public and command == "forcenextphase":
        state.nextphase()

    elif public and command == "replace":
        if len(args) == 2:
            state.replace(args[0], args[1])

    elif public and command == "showsetup" and state.channel:
        state.showsetup(who)
        bot.notice(state.channel, "%s used showsetup"%who)

    elif command == "setrole" and state.channel:
        if len(args) == 2:
            if state.setrole(args[0], args[1]):
                bot.notice(state.channel, "%s used setrole"%who)

    elif command == "dump":
        dumper.max_depth = 9
        print(dumper.dump(state))

# informational commands
    elif command == "testsetup":
        state.testsetup(args)
# public informational commands
    elif public and command == "living":
        state.livingmsg()
    elif public and command == "votes":
        state.votecount()
    elif public and command == "phase":
        state.phasemsg()
# game start cmds
    elif public and command == "start":
        state.start(to)
    elif public and command == "wait":
        state.wait()
    elif public and command == "go":
        state.go(args[0] if args else None)

    elif public and command == "starttest":
        state.gotest(to, who, args)

# role commands
    elif command:
        print("game command %s args %s"%(command,args))
        state.tryability(who, public, command, args)

    rungame(bot, public, to, who, state)

    bot.store('maf', state)

#!/usr/bin/python3
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

def nickchange(bot, before, after):
    state = bot.get('maf')
    if state:
        state.replace(before, after, True)
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
        bot.reply(to, who, "normal commands: %s" % ", ".join(["join","start","go",
                "wait","done","role","testsetup","living","votes","phase","replace",
                "dccchat", "changesetup"]))
        bot.reply(to, who, "mod commands: %s" % ", ".join(["reset",
                "force","forcep","forcenextphase","showsetup","setrole","starttest"]))

    elif public and (command == "join" or command == "start"):
        state.join(to, who, args)

    elif command == "done":
        state.done(who)

    elif command == "role":
        state.fullrolepm(who)

    elif command == "rolepower":
        state.rolepower(who, args)

# mod commands
    elif public and command == "force":
        if len(args) >= 2:
            run(bot, args[1], to, args[0], args[2:])
        state.makefake(who, args)

    elif public and command == "forcep":
        if len(args) >= 2:
            run(bot, args[1], "bot", args[0], args[2:])
        state.makefake(who, args)

    elif public and command == "forcenextphase":
        state.nextphase()

    elif public and command == "replace":
        if len(args) == 2:
            state.replace(args[0], args[1])

    elif public and command == "showsetup" and state.channel:
        state.showsetup(who)
        bot.notice(state.channel, "%s used showsetup"%who)

    elif command == "setrole" and state.channel:
        if state.setrole(who, args):
            bot.notice(state.channel, "%s used setrole"%who)

    elif command == "dump":
        dumper.max_depth = 9
        print(dumper.dump(state))

# informational commands
    elif command == "testsetup":
        bot.reply(to, who, state.testsetup(args))
# public informational commands
    elif public and command == "living":
        state.livingmsg()
    elif public and command == "dead":
        state.deadmsg()
    elif public and command == "votes":
        state.votecount()
    elif public and command == "phase":
        state.phasemsg()
# game start cmds
    elif command == "changesetup":
        state.changesetup(args)
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

if __name__ == "__main__":
    print("who to command args")
    import sys
    class TestBot:
        def __init__(self):
            self.state = {}
        def get(self, key):
            return self.state.get(key)
        def store(self, key, val):
            self.state[key] = val
        def reply(self, to, who, msg):
            print(msg)
        def notice(self, who, msg):
            print(msg)
        def privmsg(self, who, msg):
            print(msg)
    tester = TestBot()
    while True:
        line = sys.stdin.readline()
        if line:
            line = line[0:-1]
            fields = line.split(" ")
            who = fields[0]
            to = fields[1]
            command = fields[2]
            args = fields[3:]
            run(tester, command, to, who, args)
        else:
            break

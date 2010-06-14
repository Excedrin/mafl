import mafia
import traceback
from difflib import SequenceMatcher

import dumper

def fuzzy(state, tryname):
    best = 0
    match = None
    names = state.playernames()
    if tryname in names:
        return (tryname, 1, tryname)
    
    for name in filter(lambda x:len(x) > 1, names):
        ratio = SequenceMatcher(None, tryname.lower(), name.lower()).ratio()
        if ratio > best:
            best = ratio
            match = name
    return (tryname, best, match)

def cleanargs(state, args):
    return [fuzzy(state, x) for x in args]

def run(bot, command, to, who, args):
    state = bot.get('maf')

    if command == "%reset":
        state = None

    if state == None:
        state = mafia.State()

    if command == "%join":
        state.newplayer(who, None)

    elif command == "%role":
        bot.privmsg(who, role)

    elif command == "%force":
        if len(args) >= 2:
            run(bot, args[1], to, args[0], args[2:])
#        state.newplayer(args[0], None)

    elif command == "%living":
        state.livingmsg()

    elif command == "%forcenextphase":
        state.nextphase()

    elif command == "%phase":
        bot.reply(to, who, "%s" %state.phase.name)

    elif command == "%votes":
        state.votecount()

    elif command == "%replace":
        state.replace(args[0], args[1])

    elif to and to[0] == "#" and command == "%start":
        state.start(to)

    elif command == "%dump":
        print(dumper.dump(state))

    elif command and (command[0] == '%') or (to and to[0] != "#"):
        ability = command[1:]
        print("args:",args)
        player = state.playerbyname(who)
        if player:
            print("found player:",who,player)
            try:
                cleaned = []
                mangled = []
                for tryname, best, match in cleanargs(state, args):
                    if best > 0.6:
                        print("fuzzy match",tryname,best,match)
                        cleaned.append(match)
                    else:
                        mangled.append(tryname)

                if mangled:
                    bot.reply(to, who, "%s not found" %mangled)
                else:
                    if player.faction and ability in player.faction.abilities:
                        (res, msg) = player.faction.abilities[ability].use(state, player, cleaned)
                        # faction ability failed, now try player ability
                        if not res and ability in player.abilities:
                            (res, msg) = player.abilities[ability].use(state, player, cleaned)
                        bot.privmsg(who, msg)
                    elif ability in player.abilities:
                        (res, msg) = player.abilities[ability].use(state, player, cleaned)
                        bot.privmsg(who, msg)

            except Exception as e:
                print("exception trying to handle player ability: %s\n%s\n" %(ability, e))
                traceback.print_exc()

    result = state.run()
    for target, l in result:
        print("res:",target,l)
        if target:
            bot.privmsg(target, l)
        else:
            bot.privmsg(state.channel, l)

    bot.store('maf', state)

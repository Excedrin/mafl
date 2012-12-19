VERSION = "0.22"

def run(bot, command, to, who, args, authed):
#    if to[0] == '#' and command == "%version":
#        bot.privmsg(to, VERSION)
    if to == bot.nick and command == "%version":
        bot.privmsg(who, VERSION)

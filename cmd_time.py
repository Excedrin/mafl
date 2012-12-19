import time

def run(bot, command, to, who, args, authed):
    if to[0] == '#' and command == "%time":
        bot.privmsg(to, time.asctime())
    if to == bot.nick and command == "time":
        bot.privmsg(who, time.asctime())

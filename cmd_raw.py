def run(bot, command, to, who, args, authed):
    if to == bot.nick and command == "raw":
        if authed:
            bot.send(" ".join(args))
        else:
            print("raw cmd, not authed: %s %s %s" %(who, command, args))

def run(bot, command, to, who, args):
    if to == bot.nick and command == "raw":
        bot.send(" ".join(args))

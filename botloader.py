#!/usr/bin/python3
import imp
import reloader
reloader.enable()

import bot

#b = bot.Bot('irc.foonetic.net', 6667, 'mafl', 'mafl', 'mafl')
b = bot.Bot('localhost', 6668, 'mafl', 'mafl', 'mafl')
#b = bot.Bot('irc.dal.net', 6667, 'mafl', 'mafl', 'mafl')
#b = bot.Bot('irc.synirc.org', 6667, 'mafl', 'mafl', 'mafl')
quit = False

def reload(m):
    print("Reloading " + m.__file__)
    imp.reload(m)

r = reloader.Reloader(reload=reload)
#r = reloader.Reloader()

while not quit:
    (b, quit) = b.run()

    if not quit:
        try:
#            bot = reload(bot)
            r.poll()
            b = bot.Bot(b)
        except Exception as e:
            print("failed to reload: %s" % e)

#!/usr/bin/python3
import imp
import reloader
reloader.enable()

import bot

from configparser import SafeConfigParser

import sys
sys.stderr = sys.stdout

####
####
####
parser = SafeConfigParser()
parser.read('mafl.ini')

def getcfg(section, key, default):
    try:
        return parser.get(section, key)
    except:
        return default

cfg = {}

for k in parser.options('mafl'):
    cfg[k] = getcfg('mafl', k, None)

if 'network' in cfg:
    for k in parser.options(cfg['network']):
        cfg[k] = parser.get(cfg['network'], k, cfg[k])

####
####
####

b = bot.Bot(cfg)

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
            r.poll()
        except Exception as e:
            print("failed to reload: %s" % e)

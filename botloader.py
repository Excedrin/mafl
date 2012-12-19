#!/usr/bin/python3
import imp

import monitor

import bot

from configparser import SafeConfigParser

import sys
sys.stderr = sys.stdout

####
####
####
parser = SafeConfigParser()
parser.read('mafl.ini')

cfg = {}

for k in parser.options('mafl'):
    cfg[k] = parser.get('mafl', k, fallback=None)

if 'network' in cfg:
    for k in parser.options(cfg['network']):
        cfg[k] = parser.get(cfg['network'], k, fallback=cfg[k])

print(cfg)
####
####
####

b = bot.Bot(cfg)

quit = False

r = monitor.Reloader()

while not quit:
    (b, quit) = b.run()

    if not quit:
        try:
            r.poll()
        except Exception as e:
            print("failed to reload: %s" % e)

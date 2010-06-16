import time
import socket
import select
import copy
import sys
import traceback

import cmd_raw
import cmd_version
import cmd_time
import cmd_maf

import random

def clean(str):
    return str[1:]

def nick(str):
    parts = str[1:].split('!')
    return parts[0]

# this is horrible and I don't care ;_;
def colorlen(s):
    if s[0].isdigit() and s[1].isdigit() and s[2] == "," and s[3].isdigit() and s[4].isdigit():
        return 5
    if s[0].isdigit() and s[1].isdigit() and s[2] == "," and s[3].isdigit():
        return 4
    if s[0].isdigit() and s[1].isdigit() and s[2] == ",":
        return 2

    if s[0].isdigit() and s[1].isdigit():
        return 2

    if s[0].isdigit() and s[1] == "," and s[2].isdigit() and s[3].isdigit():
        return 4
    if s[0].isdigit() and s[1] == "," and s[2].isdigit():
        return 3

    if s[0] == "," and s[1].isdigit() and s[2].isdigit():
        return 3
    if s[0] == "," and s[1].isdigit():
        return 2
    if s[0].isdigit():
        return 1
    return 0

def stripcolors(s):
    r = ""
    i = 0
    while i < len(s):
        if ord(s[i]) == 3:
            if i+1 < len(s):
                z = s[i+1:]
                z += "......"
                codelen = colorlen(z)
                i += 1 + codelen
            else:
                i += 1
        else:
            r += s[i]
            i += 1
    return r

MAXCMDS = 6
class Bot():
    def __init__(self, *args):
        if len(args) == 5:
            (host, port, nick, ident, name) = args
            self.server = None

            self.s = socket.socket()
            self.connected = False

            self.host = host
            self.port = port
            self.nick = nick
            self.ident = ident
            self.name = name

            self.exit = False
            self.reload = False

            self.state = {}

            self.joined = False

            self.rng = random.Random()

# ratelimit crap
            self.lasttime = 0

            self.lastsent = 0
            self.sent = 0
            self.sentrate = 0

            self.lastrecvd = 0
            self.recvd = 0
            self.recvrate = 0

            self.prev = {}

        if len(args) == 1:
            self.state = {}
            instance = args[0]
            self.__dict__ = copy.copy(instance.__dict__)

        self.setupcmds()

    def setupcmds(self):
        self.commands = [cmd_raw, cmd_version, cmd_time, cmd_maf]

    def send(self, msg):
        if self.sentrate < 1000:
            msg = bytes(msg.encode('utf8')) + b"\r\n"
            self.sent += len(msg)
            self.s.send(msg)
        else:
            print("throttled output")

    def notice(self, to, msg):
        self.send("NOTICE %s :%s" %(to, msg))

    def privmsg(self, to, msg):
        self.send("PRIVMSG %s :%s" %(to, msg))

    def reply(self, to, who, msg):
        if to and to[0] == '#':
            self.privmsg(to, msg)
        else:
            self.privmsg(who, msg)

    def get(self, key):
        return self.state.get(key)

    def store(self, key, value):
        self.state[key] = value
    
    def connect(self):
        if not self.connected:
            self.connected = True
            self.s.connect((self.host, self.port))
            self.send('NICK %s' %self.nick)
            self.send('USER %s %s %s :%s' %(self.ident,self.ident,self.ident,self.name))
            print("connected")

    def parse(self, line):
        fields = line.split(" ")
#        print(fields)
        if not self.server:
            self.server = fields[0]
        if fields[0] == 'PING':
            msg = 'PONG ' + " ".join(fields[1:])
#            print('replying: ' + msg)
            self.send(msg)
        else:
            if fields[0] != self.server:
                if fields[0] in self.prev:
                    self.prev[fields[0]] += 1
                    if self.prev[fields[0]] == MAXCMDS:
                        print("ignored msg from",fields[0])
                        return
                    if self.prev[fields[0]] > MAXCMDS:
                        return
                else:
                    self.prev[fields[0]] = 1
        if len(fields) > 2:
            if (nick(fields[0]) == self.nick) and fields[1] == 'JOIN':
                self.joined = True
            if fields[1] == 'KICK':
                self.joined = False
            if fields[1] == 'PRIVMSG' or fields[1] == 'NOTICE':
                msg = clean(" ".join(fields[3:]))
                who = nick(fields[0])
                print("<%s> %s" %(who, msg))

                if msg == "%reload":
                    print("got reload")
#                if fields[2] == self.nick and msg == "%reload":
                    self.reload = True
                    return
                if msg == "%quit":
#                if fields[2] == self.nick and msg == "%quit":
                    self.exit = True
                    return
                noemptyargs = list(filter(lambda x: x, fields[4:]))

                for cmd in self.commands:
                    try:
                        cmd.run(self, clean(fields[3]), fields[2], who, noemptyargs)
                    except Exception as e:
                        print("exception running cmd: %s\n%s\n" %(cmd, e))
                        traceback.print_exc()

    def ratelimit(self):
        if time.time() >= self.lasttime + 1:
            self.lasttime = time.time()
        else:
            return
        self.sentrate = self.sent - self.lastsent
        self.lastsent = self.sent

        self.recvrate = self.recvd - self.lastrecvd
        self.lastrecvd = self.recvd

#        byfreq = sorted(self.prev.items(), key=lambda t: (t[1],t[0]), reverse=True)
        byfreq = list(self.prev.items())

        # 100 bytes per second is kinda arbitrary
        if self.sentrate < 100 and self.recvrate < 100:
            for k,v in byfreq:
                if v > 0:
                    self.prev[k] -= 1
                else:
                    del self.prev[k]
        else:
            print("sent",self.sentrate, "recv",self.recvrate, self.prev)

    def tick(self):
        self.ratelimit()
        # join hack
        if not self.joined:
            print("join")
            self.send('JOIN :#m')

        for cmd in self.commands:
            tick = getattr(cmd,'tick',lambda _: None)
            try:
                tick(self)
            except Exception as e:
                print("exception running cmd tick: %s\n%s\n" %(cmd, e))
                traceback.print_exc()

    def run(self):
        self.reload = False
        self.exit = False

        self.connect()
        p = select.poll()
        p.register(self.s, select.POLLIN)

        fdmap = {}
        fdmap[self.s.fileno()] = self.s

        while not self.exit and not self.reload:
            for fd,event in p.poll(1000):
                self.ratelimit()
                if event & select.POLLIN and fd in fdmap:
                    sock = fdmap[fd]
                    buf = sock.recv(4096).decode('utf8')
                    self.recvd += len(buf)
                    lines = buf.split("\r\n")
                    for line in lines:
                        if line:
                            self.parse(stripcolors(line))
                    sys.stdout.flush()
            else: # poll timeout
                self.tick()

        return (self, self.exit)

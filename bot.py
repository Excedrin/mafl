#!/usr/bin/python2
import socket
import copy
import sys
import traceback

import cmd_raw
import cmd_version
import cmd_time
import cmd_maf

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

class Bot():
    def __init__(self, *args):
        if len(args) == 5:
            (host, port, nick, ident, name) = args
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

        if len(args) == 1:
            self.state = {}
            instance = args[0]
            self.__dict__ = copy.copy(instance.__dict__)

        self.setupcmds()

    def setupcmds(self):
        self.commands = [cmd_raw, cmd_version, cmd_time, cmd_maf]

    def send(self, msg):
        self.s.send(bytes(msg.encode('utf8')) + b"\r\n")

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
            self.send('join #m')

    def parse(self, line):
        fields = line.split(" ")
#        print(fields)
        if fields[0] == 'PING':
            msg = 'PONG ' + " ".join(fields[1:])
#            print('replying: ' + msg)
            self.send(msg)
        if len(fields) > 2:
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

    def run(self):
        self.reload = False
        self.exit = False

        self.connect()
        while not self.exit and not self.reload:
            buf = self.s.recv(4096).decode('utf8')
            lines = buf.split("\r\n")
            for line in lines:
                if line:
                    self.parse(stripcolors(line))
            sys.stdout.flush()

        print("exiting or reloading")

        return (self, self.exit)

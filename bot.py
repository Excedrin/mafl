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

import re

import random

sep = re.compile(r'\r\n|\r|\n')

def clean(s):
    return s[1:]

def nick(s):
    parts = s[1:].split('!')
    return parts[0]

color = re.compile(r'[\x02\x1f\x16\x0f]|\x03\d{0,2}(?:,\d{0,2})?')

readmask = select.POLLIN | select.POLLERR | select.POLLHUP
writemask = select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLOUT

class Sock:
    def __init__(self, host, port):
        self.s = socket.socket()
        self.host = host
        self.port = port
        self.who = None
        self.nick = None

        self.queued = []

    def pollin(self):
        return None
    def mangle(self, line):
        return line
    def recv(self, size):
        return self.s.recv(size)
    def queue(self, msg):
        self.queued.append(msg)
    def send(self):
        sent = 0
        if self.queued:
            allmsg = ''.join(self.queued)
            msgbytes = bytes(allmsg.encode('utf8'))
            self.queued = []
            sent = self.s.send(msgbytes)
            if sent != len(msgbytes):
                # not really dealing with this now
                raise ValueError
        return sent
    def fileno(self):
        return self.s.fileno()
    def close(self):
        return self.s.close()

    def nickchange(self, oldnick, newnick):
        pass

class Server(Sock):
    def connect(self, nick, user, realname):
        self.s.connect((self.host, self.port))
        self.queue('NICK %s' % nick)
        self.queue('USER %s %s %s :%s' %(user, user, user, realname))
    def queue(self, msg):
        Sock.queue(self, msg + "\r\n")

class DCC(Server):
    def __init__(self, host, port, who, nick):
        Sock.__init__(self, host, port)
        self.who = who
        self.nick = nick
    def connect(self):
        self.s.connect((self.host, self.port))
    def mangle(self, line):
        mng = self.who+" PRIVMSG "+self.nick+" :"+line
        print("mangled",mng)
        return mng
    def nickchange(self, oldnick, newnick):
        userhost = self.who.split('!')[1]
        self.who = ':' + newnick + "!" + userhost

class DCCListen(DCC):
    def connect(self):
        self.s.bind((self.host, self.port))
        self.s.listen(2)

    def pollin(self):
        print("calling accept")
        (newsock, remote) = self.s.accept()
        print("connected to",remote)

        newdcc = DCC(self.host, self.port, self.who, self.nick)
        newdcc.s = newsock
        return newdcc

MAXSEND = 1000
MAXCMDS = 6
class Bot():
    def __init__(self, cfg):
        self.cfg = cfg

        self.s = None
        self.p = select.poll()

        self.server = cfg['server']
        self.port = int(cfg['port'])
        self.nick = cfg['nick']
        self.user = cfg['user']
        self.realname = cfg['realname']
        self.channel = cfg['channel']

        self.usenotice = cfg.get('usenotice', False)

        self.owner = cfg.get('owner', "")

        self.servernick = None

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

        self.setupcmds()

        self.fdmap = {}
        self.sockmap = {}


    def auth(self, src):
        print("auth: %s %s" %(self.owner, src[1:]))
        return self.owner == src[1:]

    def adduser(self, sock):
        print("adduser",nick(sock.who).lower())
        self.sockmap[nick(sock.who).lower()] = sock

    def finduser(self, nick):
        return self.sockmap.get(nick.lower(), self.s)

    def removeuser(self, nick):
        print("removeuser:",nick)
        del self.sockmap[nick.lower()]

    def nickchange(self, oldnick, newnick):
        sock = self.finduser(oldnick)
        if sock.who:
            print("nickchange:",oldnick,newnick)
            sock.nickchange(oldnick, newnick)
            self.adduser(sock)
            self.removeuser(oldnick)

    def setupcmds(self):
        self.commands = [cmd_raw, cmd_version, cmd_time, cmd_maf]

    def send(self, msg):
        self.sent += len(msg)
        self.s.queue(msg)

    def notice(self, to, msg):
        if not self.dcchack(to,msg):
            if self.usenotice:
                self.send("NOTICE %s :%s" %(to, msg))
            else:
                self.send("PRIVMSG %s :%s" %(to, msg))

    def privmsg(self, to, msg):
        if not self.dcchack(to,msg):
            self.send("PRIVMSG %s :%s" %(to, msg))

    def dcchack(self, to, msg):
        sock = self.finduser(to)
        if sock.who:
            #print("dcchack found",to) #, sock)
            sock.queue(msg)
            return True
        return False

    def reply(self, to, who, msg):
        if to and to[0] == '#':
            self.privmsg(to, msg)
        else:
            self.notice(who, msg)

    def get(self, key):
        return self.state.get(key)

    def store(self, key, value):
        self.state[key] = value

    def ipstr(self, ipstr):
        res = 0
        for o,n in zip(ipstr.split('.'), range(4)):
            res += int(o) << ((3-n) * 8)
        return res

    def parsectcp(self, who, dat, rest):
        print("ctcp: %s %s %s" %(who, dat, rest))
        #ctcp: DCC ['CHAT', 'CHAT', '2130706433', '56772']
        if dat == 'DCC' and len(rest) == 4 and rest[0] == 'CHAT':
            ipint = int(rest[2])
            port = int(rest[3])
            ipstr = "%d.%d.%d.%d" %(ipint >> 24 & 0xFF, ipint >> 16 & 0xFF,
                    ipint >> 8 & 0xFF, ipint & 0xFF)
            print("ctcp chat req %s %s %d"%(who, ipstr, port))

            sock = DCC(ipstr, port, who, self.nick)
            sock.connect()
            self.addsock(sock)

    def parse(self, line):
        fields = list(filter(None, line.split(" ")))
        if not fields:
            return
        #print(fields)
        if not self.servernick:
            self.servernick = fields[0]
        if fields[0] == 'PING':
            msg = 'PONG ' + " ".join(fields[1:])
            #print('replying: ' + msg)
            self.send(msg)
        else:
            if fields[0] != self.servernick:
                if fields[0] in self.prev:
                    self.prev[fields[0]] += 1
                    if self.sentrate > MAXSEND and self.prev[fields[0]] == MAXCMDS:
                        print("ignored msg from",fields[0])
                        return
                    if self.sentrate > MAXSEND and self.prev[fields[0]] > MAXCMDS:
                        return
                else:
                    self.prev[fields[0]] = 1

        if len(fields) > 2:
            if (nick(fields[0]) == self.nick) and fields[1] == 'JOIN':
                self.joined = True
            if fields[1] == 'KICK':
                self.joined = False

            # nickchange [':Excedrin!Excedrin@h-2033CAFE', 'NICK', ':foo']
            if fields[1] == 'NICK':
                print(fields)
                oldnick = nick(fields[0])
                newnick = nick(fields[2])
                self.nickchange(oldnick, newnick)

                for cmd in self.commands:
                    if hasattr(cmd,'nickchange'):
                        try:
                            cmd.nickchange(self, oldnick, newnick)
                        except Exception as e:
                            print("exception nickchanging cmd: %s\n%s\n" %(cmd, e))
                            traceback.print_exc()

            if fields[1] == 'PRIVMSG' or fields[1] == 'NOTICE':
                who = nick(fields[0])

                if fields[3].startswith(':\x01'):
                    # got ctcp/action
                    print("ctcp fields",fields)
                    fields[-1] = fields[-1][0:-1]
                    ctcp = fields[3][2:]
                    rest = fields[4:]
                    self.parsectcp(fields[0], ctcp, rest)
                    return

                msg = clean(" ".join(fields[3:]))
                print("<%s> %s" %(who, msg))

                if msg == "%dccchat":
                    ipstr = self.ipstr(self.cfg['dccip'])
                    port = self.rng.randint(int(self.cfg['dccminport']), int(self.cfg['dccmaxport']))
                    self.privmsg(who,"\x01DCC CHAT CHAT %s %d\x01"%(ipstr, port))
                    self.listendcc(fields[0], port)
                    print("sent dcc req",who)
                    return
                if msg == "%reload":
                    print("got reload")
                #if fields[2] == self.nick and msg == "%reload":
                    self.reload = True
                    return
                if msg == ("%quit " + self.cfg['quitpass']):
                #if fields[2] == self.nick and msg == "%quit":
                    self.exit = True
                    return
#                noemptyargs = list(filter(None, fields[4:]))

                authed = self.auth(fields[0])
                for cmd in self.commands:
                    try:
                        cmd.run(self, clean(fields[3]), fields[2], who, fields[4:], authed)
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
        if self.sentrate < 100: #and self.recvrate < 100:
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
            self.send('JOIN :%s' % self.channel)

        for cmd in self.commands:
            tick = getattr(cmd, 'tick', lambda _: None)
            try:
                tick(self)
            except Exception as e:
                print("exception running cmd tick: %s\n%s\n" %(cmd, e))
                traceback.print_exc()

        sys.stdout.flush()

    def addsock(self, s):
        self.p.register(s, readmask)
        self.fdmap[s.fileno()] = s
        if s.who:
            self.adduser(s)

    def closesock(self, sock):
        self.p.unregister(sock)
        del self.fdmap[sock.fileno()]
        sock.close()

    def listendcc(self, who, port):
        print("listen on port %d for %s"%(port, who))

        sock = DCCListen('0.0.0.0', port, who, self.nick)
        sock.connect()
        self.addsock(sock)

    def run(self):
        self.reload = False
        self.exit = False

        if not self.s:
            self.s = Server(self.server, self.port)
            self.s.connect(self.nick, self.user, self.realname)
            self.addsock(self.s)

        while not self.exit and not self.reload:
            for fd, sock in self.fdmap.items():
                if sock.queued:
                    self.p.modify(sock, writemask)
                else:
                    self.p.modify(sock, readmask)

            try:
                events = self.p.poll(1000)
            except InterruptedError as e:
                events = []

            for fd, event in events:
                if fd in self.fdmap:
                    self.ratelimit()

                    sock = self.fdmap[fd]
                    if event & select.POLLIN:
                        newsock = sock.pollin()
                        if newsock:
                            self.addsock(newsock)
                            self.closesock(sock)
                        else:
                            buf = sock.recv(4096).decode(encoding='utf-8', errors='replace')
                            if len(buf):
                                #print("recv'd", len(buf))
                                self.recvd += len(buf)
                                lines = sep.split(buf)

                                for line in lines:
                                    if line:
                                        mangled = sock.mangle(line)
                                        decolored = color.sub("", mangled)
                                        self.parse(decolored)
                            else:
                                print("disconnected sock",fd,event)
                                if sock.who:
                                    self.removeuser(nick(sock.who))
                                self.closesock(sock)
                                for msg in sock.queued:
                                    print("requeue",msg)
                                    self.privmsg(msg)

                        sys.stdout.flush()

                    if event & select.POLLHUP or event & select.POLLERR:
                        #print("got hup/err on",fd,event)
                        if sock.who:
                            self.removeuser(nick(sock.who))
                        self.closesock(sock)

                    if event & select.POLLOUT:
                        #print("got pollout on",fd,event)
                        try:
                            sock.send()
                        except socket.error as message:
                            print("exception sending to socket", message)
                else:
                    print("fd not in map",fd)

            if not events: # poll timeout
                self.tick()

        return (self, self.exit)

#dump=" ".join(["%02x"%ord(x) for x in line])
#print("dump",dump)

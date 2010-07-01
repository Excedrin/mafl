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

def clean(str):
    return str[1:]

def nick(str):
    parts = str[1:].split('!')
    return parts[0]

color = re.compile(r'[\x02\x1f\x16\x0f]|\x03\d{0,2}(?:,\d{0,2})?')

MAXSEND = 1000
MAXCMDS = 6
class Bot():
    def __init__(self, cfg):
        self.cfg = cfg

        self.s = socket.socket()
        self.connected = False

        self.server = cfg['server']
        self.port = int(cfg['port'])
        self.nick = cfg['nick']
        self.user = cfg['user']
        self.realname = cfg['realname']

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

        self.viadcc = {}
        self.fdmap = {}
        self.p = None

    def setupcmds(self):
        self.commands = [cmd_raw, cmd_version, cmd_time, cmd_maf]

    def send(self, msg):
        bmsg = bytes(msg.encode('utf8')) + b"\r\n"
        self.sent += len(bmsg)
        try:
            self.s.send(bmsg)
        except socket.error as message:
            print("exception sending to server socket",message)


    def notice(self, to, msg):
        if not self.dcchack(to,msg):
            self.send("NOTICE %s :%s" %(to, msg))

    def privmsg(self, to, msg):
        if not self.dcchack(to,msg):
            self.send("PRIVMSG %s :%s" %(to, msg))

    def dcchack(self, to, msg):
        tl = to.lower()
        res = tl in self.viadcc
        if res:
            bmsg = bytes(msg.encode('utf8')) + b"\r\n"
            try:
                self.viadcc[tl].send(bmsg)
            except socket.error as message:
                print("exception on dcc socket",message)
                dccsock = self.viadcc[tl]
                self.p.unregister(dccsock)
                del self.viadcc[tl]
                del self.fdmap[dccsock.fileno()]
                dccsock.close()

        return res

    def reply(self, to, who, msg):
        if to and to[0] == '#':
            self.privmsg(to, msg)
        else:
            self.notice(who, msg)

    def get(self, key):
        return self.state.get(key)

    def store(self, key, value):
        self.state[key] = value
    
    def connect(self):
        if not self.connected:
            self.connected = True
            self.s.connect((self.server, self.port))
            self.send('NICK %s' %self.nick)
            self.send('USER %s %s %s :%s' %(self.user,self.user,self.user,self.realname))
            print("connected")

    def ipstr(self, ipstr):
        res = 0
        for o,n in zip(ipstr.split('.'), range(4)):
            res += int(o) << ((3-n) * 8)
        return res

    def listendcc(self, who, port):
        print("listen on port %d for %s"%(port, who))
        s = socket.socket()
        s.bind(('0.0.0.0', port))
        s.listen(2)
        (newsock, remote) = s.accept()
        self.viadcc[nick(who).lower()] = newsock
        self.fdmap[newsock.fileno()] = (who, newsock)
        self.p.register(newsock, select.POLLIN | select.POLLERR | select.POLLHUP)
        print("connected to",remote)
        s.close()

    def parsectcp(self, who, dat, rest):
        print("ctcp: %s %s %s" %(who, dat,rest))
        #ctcp: DCC ['CHAT', 'CHAT', '2130706433', '56772']
        if dat == 'DCC' and len(rest) == 4 and rest[0] == 'CHAT':
            ipint = int(rest[2])
            port = int(rest[3])
            ipstr = "%d.%d.%d.%d" %(ipint >> 24  & 0xFF, ipint >> 16  & 0xFF,
                    ipint >> 8 & 0xFF, ipint & 0xFF)
            print("ctcp chat req %s %s %d"%(who, ipstr, port))
            newsock = socket.socket()
            try:
                newsock.connect((ipstr, port))
                self.viadcc[nick(who).lower()] = newsock
                self.fdmap[newsock.fileno()] = (who, newsock)
                self.p.register(newsock, select.POLLIN | select.POLLERR | select.POLLHUP)
                print("connected")
            except socket.error as message:
                print("dcc chat error",message)

    def parse(self, line):
        fields = line.split(" ")
#        print(fields)
        if not self.servernick:
            self.servernick = fields[0]
        if fields[0] == 'PING':
            msg = 'PONG ' + " ".join(fields[1:])
#            print('replying: ' + msg)
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
                (oldnick, userhost) = fields[0][1:].split('!')
                newwho = ':' + fields[2] + userhost
                newnick = fields[2][1:]

                if nick(fields[0]) in self.viadcc:
                    dccsock = self.viadcc[oldnick]
                    self.fdmap[dccsock.fileno()] = (newwho, dccsock)
                    self.viadcc[newnick] = dccsock
                    del self.viadcc[oldnick]

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
                    ctcp = fields[3][2:]
                    rest = fields[4:]
                    rest[-1] = rest[-1][0:-1]
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
#                if fields[2] == self.nick and msg == "%reload":
                    self.reload = True
                    return
                if msg == ("%quit " + self.cfg['quitpass']):
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
            self.send('JOIN :#m')

        for cmd in self.commands:
            tick = getattr(cmd,'tick',lambda _: None)
            try:
                tick(self)
            except Exception as e:
                print("exception running cmd tick: %s\n%s\n" %(cmd, e))
                traceback.print_exc()

        sys.stdout.flush()

    def run(self):
        self.reload = False
        self.exit = False

        self.connect()

        self.p = select.poll()
        self.p.register(self.s, select.POLLIN | select.POLLERR | select.POLLHUP)

        self.fdmap = {}
        self.fdmap[self.s.fileno()] = (None, self.s)

        while not self.exit and not self.reload:
            for fd,event in self.p.poll(1000):
                if fd in self.fdmap:
                    self.ratelimit()
                    (dcc, sock) = self.fdmap[fd]
                    if event & select.POLLIN:
                        buf = sock.recv(4096).decode('utf8')
                        self.recvd += len(buf)
                        lines = sep.split(buf)
                        for line in lines:
                            if line:
                                #dump=" ".join(["%02x"%ord(x) for x in line])
                                #print("dump",dump)
                                if dcc:
                                    line = dcc+" PRIVMSG "+self.nick+" :"+line
                                    #print("hax dcc line",line)
                                self.parse(color.sub("",line))
                        sys.stdout.flush()
                    elif event & (select.POLLHUP|select.POLLERR):
                        print("got hup/err on ",fd)
                        if dcc and nick(dcc) in self.viadcc:
                            del self.viadcc[nick(dcc)]
                else:
                    print("fd not in map",fd)
                    

            else: # poll timeout
                self.tick()

        return (self, self.exit)

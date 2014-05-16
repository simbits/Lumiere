#!/usr/bin/env python

import random
import socket
import struct
import sys
import time

CABINET_VERSION='1.0c'
START_MSG='## Cabinet test version %s ##' % (CABINET_VERSION) 

MCAST_GRP = ('224.19.79.1', 9999)
DRAWERS = 9
RETRIGGER_DELAY = 10    #seconds
WAIT_DELAY = 3        #seconds

opened = [False] * DRAWERS

if __name__ == '__main__':
    print 'setting up mcast group @%s' % (str(MCAST_GRP))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    print opened

    try:
        sock.sendto(START_MSG, MCAST_GRP)
    except Exception as e:
        print 'exception during send: %s' % (str(e))
        sys.exit(1)

    while True:
        try:
            drawer = random.randint(0, DRAWERS)
            opened[drawer] = not opened[drawer]
            if opened[drawer]:
                print 'sending opened drawer %d' % (drawer)
                sendstr = 'o:%d' % drawer
            else:
                print 'sending closing drawer %d' % (drawer)
                sendstr = 'c:%d' % drawer
            try:
                sock.sendto(sendstr, MCAST_GRP)
            except Exception as e:
                print 'exception during send: %s' % (str(e))
        except IndexError:
            pass

        time.sleep(WAIT_DELAY) # relax a little

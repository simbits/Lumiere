#!/usr/bin/env python

import random
import socket
import struct
import sys
import time

from Adafruit_MCP230xx import Adafruit_MCP230XX

CABINET_VERSION='1.0b'
START_MSG='## Cabinet version %s ##' % (CABINET_VERSION) 

MCAST_GRP = ('224.19.79.1', 9999)
DRAWERS = 9
USE_PULLUPS = 1
RETRIGGER_DELAY = 10    #seconds
WAIT_DELAY = 3        #seconds


if __name__ == '__main__':
    mcp = Adafruit_MCP230XX(address=0x20, num_gpios=16) # MCP23017
    c_state = [True] * DRAWERS
    p_state = [True] * DRAWERS
    trigger_delay = [0] * DRAWERS

    for i in range(0, DRAWERS):
        mcp.config(i, mcp.INPUT)
        mcp.pullup(i, USE_PULLUPS)
        p_state[i] = bool((mcp.input(i) >> i) & 0x01)

    print 'initial state: %s' % (str(p_state))
    print 'setting up mcast group @%s' % (str(MCAST_GRP))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        sock.sendto(START_MSG, MCAST_GRP)
    except Exception as e:
        print 'exception during send: %s' % (str(e))
        sys.exit(1)

    while True:
        for i in range(0, DRAWERS):
            if trigger_delay[i] > 0:
                trigger_delay[i] = trigger_delay[i] - 1
            #c_state[i] = bool((mcp.input(i) >> i) & 0x01)
            c_state[i] = bool(random.randint(0,1))

        triggered = {i for i in range(0, DRAWERS)
                                if c_state[i] != p_state[i] and 
                                not c_state[i] and
                                trigger_delay[i] == 0}

        closed = {i for i in range(0, DRAWERS)
                             if c_state[i] != p_state[i] and
                             c_state[i]}

        for i in triggered:
            trigger_delay[i] = RETRIGGER_DELAY / WAIT_DELAY


        print 'prev: %s' % (p_state)
        print 'cur : %s' % (c_state)
        print 'd: %s' % (trigger_delay)
        print 't: %s' % (triggered)
        print 'c: %s' % (closed)

        try:
            for i in closed:
                print 'sending closed drawer: %d' % (i)
                sock.sendto('c:%d' % (i), MCAST_GRP)
            drawer = random.choice(list(triggered))
            print 'sending opened drawer %d' % (drawer)
            sock.sendto('o:%d' % (drawer), MCAST_GRP)
        except IndexError:
            pass
        except Exception as e:
            print 'exception during send: %s' % (str(e))

        p_state = list(c_state)

        time.sleep(WAIT_DELAY) # relax a little

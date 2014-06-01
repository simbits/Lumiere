#!/usr/bin/env python

import random
import socket
import struct
import sys
import time

CABINET_VERSION='1.0b'
START_MSG='## Cabinet version %s ##' % (CABINET_VERSION)

MCAST_GRP = ('224.19.79.1', 9999)
DRAWERS = 9
USE_PULLUPS = 1
WAIT_DELAY = 0.5        #seconds

count = 0

if __name__ == '__main__':
    c_state = [True] * DRAWERS
    p_state = [True] * DRAWERS
    trigger_delay = [0] * DRAWERS

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
        try:
            if count == 10:
                print ''
                print '-------'
                print ' i: all drawers closed'
                print ' e: open drawer 5'
                print ' p: [5]'
                print ' r: play movie 5'
                c_state = [ True, True, True, True, False, True, True, True, True ]

            #if count == 10:
            #    print ''
            #    print '-------'
            #    print ' i: all drawers closed'
            #    print ' e: open drawer 1'
            #    print ' p: [1]'
            #    print ' r: play movie 1'
            #    c_state = [ False, True, True, True, True, True, True, True, True ]
            #if count == 50:
            #    print ''
            #    print '-------'
            #    print ' i: drawer 1 open'
            #    print ' e: open drawer 3'
            #    print ' p: [1,3]'
            #    print ' r: stop movie 1, play movie 3'
            #    c_state = [ False, True, False, True, True, True, True, True, True ]
            #if count == 100:
            #    print ''
            #    print '-------'
            #    print ' i: drawer 1, 3 open'
            #    print ' e: open drawer 5'
            #    print ' p: [1,3,5]'
            #    print ' r: stop movie 3, play movie 5'
            #    c_state = [ False, True, False, True, False, True, True, True, True ]
            #if count == 150:
            #    print ''
            #    print '-------'
            #    print ' i: drawer 1, 3, 5 open'
            #    print ' e: close drawer 5'
            #    print ' p: [1, 3]'
            #    print ' r: stop movie 5, start random movie from playlist'
            #    c_state = [ False, True, False, True, True, True, True, True, True ]
            #if count == 200:
            #    print ''
            #    print '-------'
            #    print ' i: drawer 1, 3 open'
            #    print ' e: close all drawers'
            #    print ' p: []'
            #    print ' r: stop current playing movie, shut off projector'
            #    c_state = [ True, True, True, True, True, True, True, True, True ]
            #if count == 250:
            #    print ''
            #    print '-------'
            #    print ' i: all drawers are closed'
            #    print ' e: drawer 6, 7, 8 opened'
            #    print ' p: [6, 7, 8]'
            #    print ' r: enablel projector, start random movie from playlist'
            #    c_state = [ True, True, True, True, True, False, False, False, True ]
            #if count == 300:
            #    print ''
            #    print '-------'
            #    print ' i: all drawers are closed'
            #    print ' e: drawer 6, 7, 8 opened'
            #    print ' p: [6, 7, 8]'
            #    print ' r: enablel projector, start random movie from playlist'
            #    c_state = [ True, True, True, True, True, False, False, True, True ]

            print 'sending drawer states %s' % (c_state)
            sock.sendto('s:%s' % (','.join(['%d' % i for i in c_state])), MCAST_GRP)
        except IndexError:
            pass
        except Exception as e:
            print 'exception during send: %s' % (str(e))

        p_state = list(c_state)

        count += 1
        time.sleep(WAIT_DELAY) # relax a little

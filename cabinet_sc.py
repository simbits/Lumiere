#!/usr/bin/env python

import random
import socket
import struct
import sys
import time

from Adafruit_MCP230xx import Adafruit_MCP230XX

CABINET_VERSION='1.0b'
START_MSG='## Cabinet version %s (SC) ##' % (CABINET_VERSION)

LUMIERE_IP = ['192.168.20.10', '192.168.20.11', '192.168.20.12']
LUMIERE_PORT = 9999
DRAWERS = 9
USE_PULLUPS = 1
WAIT_DELAY = 0.5        #seconds


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
    print 'initializing UDP socket'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)

    try:
        for ip in LUMIERE_IP:
            sock.sendto(START_MSG, (ip, LUMIERE_PORT))
    except Exception as e:
        print 'exception during send: %s' % (str(e))
        sys.exit(1)

    while True:
        for i in range(0, DRAWERS):
            c_state[i] = not bool((mcp.input(i) >> i) & 0x01)

        changed = {i for i in range(0, DRAWERS) if c_state[i] != p_state[i]}

        try:
            if len(changed) > 0:
                print 'sending drawer states %s' % (c_state)
            for ip in LUMIERE_IP:
                sock.sendto('s:%s' % (','.join(['%d' % i for i in c_state])), (ip, LUMIERE_PORT))
        except IndexError:
            pass
        except Exception as e:
            print 'exception during send: %s' % (str(e))

        p_state = list(c_state)

        time.sleep(WAIT_DELAY) # relax a little

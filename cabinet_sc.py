#!/usr/bin/env python

import random
import socket
import struct
import sys
import time

from Adafruit_MCP230xx import Adafruit_MCP230XX

CABINET_VERSION='1.0b'
START_MSG='## Cabinet version %s (SC) ##' % (CABINET_VERSION)

LUMIERE_IP = ['192.168.20.10', '192.168.20.11', '192.168.20.12', '192.168.20.100']
LUMIERE_PORT = 9999
DRAWERS = 9
USE_PULLUPS = 1
WAIT_DELAY = 0.5        #seconds
DEBOUNCE_DELAY_COUNT    2

if __name__ == '__main__':
    mcp = Adafruit_MCP230XX(address=0x20, num_gpios=16) # MCP23017
    c_state = [True] * DRAWERS
    p_state = [True] * DRAWERS
    delay_list = [-1] * DRAWERS
    trigger_delay = [0] * DRAWERS

    for i in range(0, DRAWERS):
        mcp.config(i, mcp.INPUT)
        mcp.pullup(i, USE_PULLUPS)
        p_state[i] = bool((mcp.input(i) >> i) & 0x01)
    c_state = list(p_state)

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
            c_state[i] = bool((mcp.input(i) >> i) & 0x01)
            if c_state[i] != p_state[i]:
                if delay_list[i] > 0:
                    delay_list[i] -= 1
                elif delay_list[i] == 0:
                    p_state[i] = c_state[i]
                    delay_list[i] = -1
                else:
                    delay_list[i] = DEBOUNCE_DELAY_COUNT
            else:
                if delay_list[i] >= 0:
                    delay_list[i] = -1

        try:
            print 'DELAY states %s' % (delay_list)
            print 'CURRENT states %s' % (c_state)
            print 'SENDING states %s' % (p_state)
            print ' ---- '

            for ip in LUMIERE_IP:
                sock.sendto('s:%s' % (','.join(['%d' % i for i in p_state])), (ip, LUMIERE_PORT))
        except IndexError:
            pass
        except Exception as e:
            print 'exception during send: %s' % (str(e))

        time.sleep(WAIT_DELAY) # relax a little

#!/usr/bin/env python

import random
import socket
import struct
import sys
import time

CABINET_VERSION='1.0b'
START_MSG='## Cabinet version %s (SC) ##' % (CABINET_VERSION)

#LUMIERE_IP = ['192.168.20.10', '192.168.20.11', '192.168.20.12']
LUMIERE_IP = ['127.0.0.1']
LUMIERE_PORT = 9999
DRAWERS = 9
USE_PULLUPS = 1
WAIT_DELAY = 0.5        #seconds
DEBOUNCE_DELAY_COUNT = 1


if __name__ == '__main__':
    c_state = [True] * DRAWERS
    p_state = [True] * DRAWERS
    delay_list = [-1] * DRAWERS

    test_states = [{'n': 1, 'delay':1, 'states':[True, False, True, False, True, False, True, False, True]},
                   {'n': 2, 'delay':1, 'states':[True, True, True, False, True, False, True, False, True]},
                   {'n': 3, 'delay':4, 'states':[True, False, True, False, True, False, True, False, True]},
                   {'n': 4, 'delay':1, 'states':[False, False, True, False, True, False, True, False, True]},
                   {'n': 5, 'delay':3, 'states':[False, False, True, False, True, False, True, False, True]},
                   {'n': 6, 'delay':3, 'states':[False, False, False, False, True, False, True, False, True]},
                   {'n': 7, 'delay':1, 'states':[True, False, True, True, True, False, True, False, True]},
                   {'n': 8, 'delay':1, 'states':[True, True, True, True, True, False, True, False, True]},
                   {'n': 9, 'delay':1, 'states':[True, True, True, True, True, False, True, False, True]},
                   {'n': 10, 'delay':1, 'states':[True, True, True, False, True, False, True, False, True]},
                   {'n': 11, 'delay':1, 'states':[True, True, True, False, True, False, True, False, True]},
                   {'n': 12, 'delay':1, 'states':[True, True, True, False, True, False, True, False, True]},
                   {'n': 13, 'delay':1, 'states':[True, True, True, False, True, False, True, False, True]},
                   {'n': 14, 'delay':5, 'states':[True, True, True, True, True, True, True, True, True]}]

    p_state = list(test_states[0]['states'])
    c_state = list(p_state)
    s_state = list(p_state)

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

    counts = 0
    testline = 0

    while True:
        counts +=1

        if counts > test_states[testline]['delay']:
            counts = 0
            testline += 1

            if testline >= len(test_states):
                print '+++ rewind'
                testline = 0

            print 'current state: %.2d' % (test_states[testline]['n'])
            c_state = list(test_states[testline]['states'])

        for i in range(0, DRAWERS):
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

        #p_state = list(c_state)

        time.sleep(WAIT_DELAY) # relax a little

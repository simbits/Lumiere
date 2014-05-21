#!/usr/bin/env python

from pyomxplayer import OMXPlayer
import RPi.GPIO as GPIO

import random
import socket
import time

MCAST_GRP = '224.19.79.1'
MCAST_PORT = 9999
MOVIE_PATH = '/usr/share/lumiere'
MOVIE_SUFFIX = 'mp4'
MOVIE_LIST = [ '%s/%d/%s' % (MOVIE_PATH, n, MOVIE_SUFFIX) for n in range(1, 10) ]

PROJECTOR_SUPPLY_PIN = 12
PROJECTOR_ON = False
PROJECTOR_OFF = True

STATE_OPEN = 'o'
STATE_CLOSED = 'c'

playlist = set()

def main():
    now_playing = None

    GPIO.setup(PROJECTOR_SUPPLY_PIN, GPIO.OUT)
    GPIO.output(PROJECTOR_SUPPLY_PIN, PROJECTOR_OFF)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except AttributeError:
        pass

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    host = '0.0.0.0'
    sock.bind((MCAST_GRP, MCAST_PORT))
    sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
    sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                    socket.inet_aton(MCAST_GRP) + socket.inet_aton(host))

    random.seed()

    while 1:
        try:
            data, addr = sock.recvfrom(512)
        except socket.error, e:
            print 'Expection: %s' % str(e)

        print '[%s] | recv (%s): %s' % (time.ctime(), addr, data)
        
        if len(data) != 3:
            print 'expected 3 bytes got %d' % len(data)
            continue
        
        try:
            state,drawer = data.split(':')
        except ValueError:
            print 'wrong data format: %s' % (data)
            continue

        if state == STATE_OPEN:
            if drawer not in playlist or not drawer == now_playing:
                playlist.add(drawer)
                # TODO: stop current playing movie?
                # TODO: play newly opened drawer
        elif state == STATE_CLOSED:
            if drawer in playlist:
                if drawer == now_playing:
                    # TODO: stop playing ?
                    now_playing = None
                playlist.remove(drawer)
                try:
                    play = random.choice(list(playlist))
                    # TODO: play new file
                except IndexError:
                    print 'playlist empty'
                    pass
    
        print playlist
        if now_playing:
            print MOVIE_LIST[now_playing]

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BOARD)
        main()
    except KeyboardInterrupt:
        print 'Exiting'
    except Exception, e:
        print 'Caught exception: %s' % str(e)
    finally:
        print 'Cleaning up GPIO settings'
        GPIO.cleanup()

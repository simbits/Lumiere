#!/usr/bin/env python

import pprint
import random
import socket
import struct
import sys
import time
import traceback

DRAWERS = 9
MCAST_GRP = '224.19.79.1'
MCAST_PORT = 9999
MOVIE_PATH = '/usr/share/lumiere/media'
MOVIE_SUFFIX = 'mp4'
MOVIE_LIST = [ '%s/%d.%s' % (MOVIE_PATH, n, MOVIE_SUFFIX) for n in range(1, 10) ]

PROJECTOR_SUPPLY_PIN = 26 #BOARD P1 pin number corresponds with GPIO7 on Rev2 RPi
PROJECTOR_ON = False
PROJECTOR_OFF = True

STATE_OPEN = 'o'
STATE_CLOSED = 'c'

_now_playing = -1

def stop_movie():
    global _now_playing

    print 'Stopping movie %d:%s' % (_now_playing+1, MOVIE_LIST[_now_playing])
    _now_playing =-1

def start_movie(index):
    global _now_playing

    if index >= len(MOVIE_LIST):
        return -1

    stop_movie()

    print 'Starting movie %d:%s' % (index+1, MOVIE_LIST[index])

    _now_playing = index

    return index

def start_random_movie_from_list(l=[]):
    try:
        return start_movie(random.choice(l))
    except IndexError:
        pass

    return -1

def is_movie_playing():

    return False

def current_movie_playing():
    global _now_playing
    return _now_playing

def main():
    previous_state = [True] * DRAWERS
    playlist = set()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    try:
        host = '0.0.0.0'
        timeval=struct.pack("2I", 0, 500000) # timeout 0.5s
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                        socket.inet_aton(MCAST_GRP) + socket.inet_aton(host))
        sock.bind((MCAST_GRP, MCAST_PORT))
    except AttributeError:
        pass

    random.seed()

    while 1:
        drawer = -1
        data = ''

        try:
            data, addr = sock.recvfrom(512)
            print '[%s] | received from %s: %s' % (time.ctime(), addr, data)

        except socket.error, e:
            if e.errno == 11:
                if not is_movie_playing():
                    start_random_movie_from_list(list(playlist))
            else:
                print 'Expection: %s' % str(e)
            continue

        try:
            if len(data) != 19:
                print 'expected 19 bytes got %d' % len(data)
                continue

            cmd,args = data.split(':')
        except ValueError, e:
            print 'wrong data format: %s (%s)' % (data, str(e))
            continue

        if cmd == 's':
            new_state = [bool(int(i)) for i in args.split(',')]

        opened = {i for i in range(0, DRAWERS)
                                if new_state[i] != previous_state[i] and
                                not new_state[i]}
        closed = {i for i in range(0, DRAWERS)
                                if new_state[i] != previous_state[i] and
                                new_state[i]}

        start_random = False
        start_new = False

        if len(opened) > 0:
            print 'New opened: %s' % (str(opened))
        if len(closed) > 0:
            print 'New closed: %s' % (str(closed))

        try:
            for i in closed:
                if i in playlist:
                    playlist.remove(i)
                    if i == current_movie_playing():
                        stop_movie()
                        start_random = True
                    if len(playlist) == 0:
                        pass
#                        GPIO.output(PROJECTOR_SUPPLY_PIN, PROJECTOR_OFF)
            if len(closed) > 0:
                print 'playlist after closing: %s' % (list(playlist))
        except IndexError:
            pass

        try:
            for i in opened:
                if i not in playlist:
                    playlist.add(i)
                    start_new = True
            if len(opened) > 0:
                print 'playlist after opening: %s' % (list(playlist))
        except IndexError:
            pass

        try:
            if start_new:
                print 'starting new movie from opened list'
                start_random_movie_from_list(list(opened))
            elif start_random:
                print 'starting random movie'
                start_random_movie_from_list(list(playlist))
            elif not is_movie_playing():
                start_movie(random.choice(list(playlist)))
        except IndexError:
            pass

        previous_state = list(new_state)

if __name__ == '__main__':
    try:
#        GPIO.setmode(GPIO.BOARD)
#        GPIO.setup(PROJECTOR_SUPPLY_PIN, GPIO.OUT)
#        GPIO.output(PROJECTOR_SUPPLY_PIN, PROJECTOR_OFF)
        main()
    except KeyboardInterrupt:
        print 'Exiting'
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    finally:
        print 'Cleaning up GPIO settings'
        stop_movie()
#        GPIO.output(PROJECTOR_SUPPLY_PIN, PROJECTOR_OFF)
        #GPIO.cleanup()

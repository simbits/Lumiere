#!/bin/bash

LUMIERE_PATH=/opt/Lumiere
BULB_BIN=$LUMIERE_PATH/bulb/bulb.py
PYTHON=/usr/bin/python
MCAST_ADDR=224.19.79.1
GW_ADDR=192.168.20.1
GW_DEV=wlan0

add_mcast_route ()
{
    route add $MCAST_ADDR gw $GW_ADDR dev $GW_DEV
}

have_wired_network ()
{
    ifconfig eth0 | grep -q inet
    return $?
}

update_lumiere ()
{
    echo "updating lumiere"
    pushd $LUMIERE_PATH > /dev/null
    git pull origin master
    popd > /dev/null
    echo "done"
}

if have_wired_network
then
    update_lumiere
fi

add_mcast_route

while :
do
    $PYTHON $BULB_BIN
    sleep 5
done

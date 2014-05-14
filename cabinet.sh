#!/bin/bash

CABINET_PATH=/opt/lumiere/cabinet
CABINET_BIN=$CABINET_PATH/cabinet.py
PYTHON=/usr/bin/python
MCAST_ADDR=224.19.79.1

add_mcast_route ()
{
    route add $MCAST_ADDR gw 192.168.20.1 dev wlan0
}

have_wired_network ()
{
    ifconfig eth0 | grep -q inet
    return $?
}

update_cabinet ()
{
    echo "updating cabinet"
    pushd $CABINET_PATH > /dev/null
    git pull origin master
    popd > /dev/null
    echo "done"
}

if have_wired_network
then
    update_cabinet
fi

add_mcast_route

while :
do
    $PYTHON $CABINET_BIN
    sleep 5
done

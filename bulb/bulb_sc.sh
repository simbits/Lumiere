#!/bin/bash

LUMIERE_PATH=/opt/Lumiere
BULB_BIN=$LUMIERE_PATH/bulb/bulb_sc.py
PYTHON=/usr/bin/python

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

while :
do
    $PYTHON $BULB_BIN
    sleep 5
done

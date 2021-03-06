#!/bin/bash

CABINET_PATH=/opt/lumiere/cabinet
CABINET_BIN=$CABINET_PATH/cabinet_sc.py
PYTHON=/usr/bin/python

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

while :
do
    $PYTHON $CABINET_BIN
    sleep 5
done

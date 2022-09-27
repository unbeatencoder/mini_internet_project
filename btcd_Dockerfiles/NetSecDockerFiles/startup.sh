#!/bin/bash

set -e

####start up necesarry daemons####

#BTC
bitcoind -daemon

#SSH
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config
mkdir -p /var/run/sshd
chmod 0755 /var/run/sshd
/usr/sbin/sshd

### ensure they start properly ###
sleep 4

# import env name
NAME=$RANDOM
export NAME=$NAME

# make wallet and readback info
echo $NAME
bitcoin-cli createwallet $NAME
bitcoin-cli -getinfo
#launch a shell so it keeps alive forever
/bin/bash

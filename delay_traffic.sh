# usage: inject_delay.sh -i ext_2_ZURI -a 2.101.0.0/24 -d 100ms
# i : interface
# a : IP address/ prefix
# d : delay

#!/bin/bash

# variables
ip=
delay=
interface=

# Get the options
while getopts "i:a:d:" option; do
   case $option in
      i) # Enter a name
         interface=$OPTARG;;
      a) # ip 
         ip=$OPTARG;;
      d) # delau
         delay=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

# echo "i = $i"
# echo "ip = $ip"
# echo "d = $delay"

tc qdisc add dev $interface root handle 1: prio
tc filter add dev $interface parent 1:0 protocol ip prio 1 u32 match ip dst $ip flowid 2:1
tc qdisc add dev $interface parent 1:1 handle 2: netem delay $delay

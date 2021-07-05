#!/bin/bash

sudo ip link add link ens33 address 00:11:11:11:11:11 virtual0 type macvlan
sudo ifconfig virtual0 up
sudo ifconfig ens33 promisc

sudo ifconfig virtual0 192.168.1.200 netmask 255.255.255.0 up
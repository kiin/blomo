#!/bin/bash

sudo pip3 install .

sudo python3.8 blomo/main.py --intf virtual0 --ip 192.168.1.200 --targets 192.168.1.201,192.168.1.202,192.168.1.203

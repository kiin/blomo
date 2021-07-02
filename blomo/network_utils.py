#!/usr/bin/env python3

import socket
import array
import struct
import fcntl
import sys


def get_local_interfaces():
    """ Returns a dictionary of name:ip key value pairs. """
    return socket.if_nameindex()

def get_mac_addr(intf):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(intf, 'utf-8')[:15]))
    return ':'.join('%02x' % b for b in info[18:24])

def create_raw_socket(intf):
    s = socket.socket( socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((intf, 0))
    except socket.error as msg:
        print(f"Couldnt connect with the socket-server: {msg}\n terminating program")
        sys.exit(1)
    return s

def ethernet_unpack(data):
    dest_mac, src_mac, eth_proto = struct.unpack("! 6s 6s H", data[:14])
    return get_mac(dest_mac), get_mac(src_mac), socket.htons(eth_proto),  data[14:]

def get_mac(mac_bytes):
    mac = map("{:02x}".format, mac_bytes)
    return (":".join(mac)).upper()
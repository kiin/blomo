#!/usr/bin/env python3

import socket
import struct
import fcntl
import sys

from enum import Enum


class EtherType(Enum):
    ARP = 2054
    IPV4 = 2048
    IPV6 = 34525


class IpProto(Enum):
    TCP = 6
    UDP = 17


def get_local_interfaces():
    """Returns a List of index:intf_name key value pairs."""
    return socket.if_nameindex()


def create_raw_socket(intf):
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((intf, 0))
    except socket.error as msg:
        print(f"Couldnt connect with the socket-server: {msg}\n terminating program")
        sys.exit(1)
    return s


def tcp_unpack(data):
    (
        source_port,
        destination_port,
        sequence_number,
        ack_number,
        header_length_reserved_flags,
        window_size,
        chucksum,
        urgent_pointer,
    ) = struct.unpack("!HHIIHHHH", data[:20])

    header_length = (
        header_length_reserved_flags >> 12
    ) * 4  # * 4 is to get the value in Bytes

    return (
        source_port,
        destination_port,
        sequence_number,
        ack_number,
        header_length,
        window_size,
        chucksum,
        urgent_pointer,
        data[header_length:],
    )


def ipv4_unpack(data):
    (
        version_header_length,
        tos,
        total_len,
        identification,
        flags_offset,
        TTL,
        ip_proto,
        header_checksum,
        source_ip,
        destination_ip,
    ) = struct.unpack("!BBHHHBBH4s4s", data[:20])
    # Black magic
    version = version_header_length >> 4
    header_length = (
        version_header_length & 15
    ) * 4  # * 4 is to have the value in Bytes

    # Extracting x_bit, Do Not Fragment Flag and More Fragments Follow Flag.
    x_bit = (flags_offset >> 15) & 1
    DFF = (flags_offset >> 14) & 1
    MFF = (flags_offset >> 13) & 1

    # Extracting Fragment Offset
    frag_offset = flags_offset & 8191

    return (
        version,
        header_length,
        tos,
        total_len,
        identification,
        x_bit,
        DFF,
        MFF,
        frag_offset,
        TTL,
        ip_proto,
        header_checksum,
        get_ipv4(source_ip),
        get_ipv4(destination_ip),
        data[header_length:],
    )


def ethernet_unpack(data):
    dest_mac, src_mac, eth_type = struct.unpack("!6s6sH", data[:14])
    return get_mac(dest_mac), get_mac(src_mac), eth_type, data[14:]


def get_mac_addr(intf):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(
        s.fileno(), 0x8927, struct.pack("256s", bytes(intf, "utf-8")[:15])
    )
    return ":".join("%02x" % b for b in info[18:24])


def get_mac(mac_bytes):
    mac = map("{:02x}".format, mac_bytes)
    return (":".join(mac)).upper()


def get_ipv4(ip_bytes):
    return ".".join(map(str, ip_bytes))

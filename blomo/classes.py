#!/usr/bin/env python3

import json


class Frame:
    def __init__(self, dest_mac, src_mac, eth_type, data) -> None:
        self.destination_mac_address = dest_mac
        self.source_mac_address = src_mac
        self.type = eth_type
        self.raw_data = data

    def to_dict(self):
        return {
            "destination_mac": self.destination_mac_address,
            "source_mac": self.source_mac_address,
            "ethernet_type": self.type,
        }


class Packet:
    def __init__(
        self,
        ip_version,
        header_len,
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
        destination_ip,
        source_ip,
        data,
    ) -> None:
        self.ip_version = ip_version
        self.header_len = header_len
        self.total_len = total_len
        self.TTL = TTL
        self.ip_proto = ip_proto
        self.destination_ip = destination_ip
        self.source_ip = source_ip
        self.raw_data = data

    def to_dict(self):
        return {
            "version": self.ip_version,
            "header_length": self.header_len,
            "header_total_length": self.total_len,
            "time_to_live": self.TTL,
            "protocol": self.ip_proto,
            "destination_ip": self.destination_ip,
            "source_ip": self.source_ip,
        }


class Segment:
    def __init__(
        self,
        source_port,
        destination_port,
        sequence_number,
        ack_number,
        header_length,
        window_size,
        chucksum,
        urgent_pointer,
        data,
    ) -> None:
        self.destination_port = destination_port
        self.source_port = source_port
        self.header_length = header_length
        self.raw_data = data

    def to_dict(self):
        return {
            "destination_port": self.destination_port,
            "source_port": self.source_port,
            "header_length": self.header_length,
        }

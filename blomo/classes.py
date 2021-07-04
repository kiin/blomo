#!/usr/bin/env python3

"""
Module to store classes used across the package.

Bogdan Lozhkin
"""

import json


class Serializer:
    """JSON serialisation mixin class.
    Classes that inherit from this class should implement `to_dict` and
    `from_dict` methods.
    """

    def to_dict(self):
        """Serialises class to dict."""
        raise NotImplementedError

    @classmethod
    def from_dict(self, d):
        """Loads class from dict."""
        raise NotImplementedError

    def to_json(self, fp=None, **kwargs):
        """Serialises class to JSON."""
        d = self.to_dict()
        if fp:
            json.dump(d, fp, **kwargs)
        else:
            return json.dumps(d, **kwargs)

    @classmethod
    def from_json(cls, js):
        """Instantiates class from JSON handle."""
        if isinstance(js, str):
            d = json.loads(js)
        else:
            d = json.load(js)
        return cls.from_dict(d)


class EtherFrame(Serializer):
    def __init__(
        self,
        dest_mac,
        src_mac,
        eth_type,
        ip_version,
        header_len,
        total_len,
        TTL,
        ip_proto,
        destination_ip,
        source_ip,
        destination_port,
        source_port,
        header_length,
    ) -> None:
        self.dest_mac = dest_mac
        self.src_mac = src_mac
        self.eth_type = eth_type
        self.ip_version = ip_version
        self.header_len = header_len
        self.total_len = total_len
        self.TTL = TTL
        self.ip_proto = ip_proto
        self.destination_ip = destination_ip
        self.source_ip = source_ip
        self.destination_port = destination_port
        self.source_port = source_port
        self.header_length = header_length

    def to_dict(self):
        return {
            "destination_mac": self.dest_mac,
            "source_mac": self.src_mac,
            "ethernet_type": self.eth_type,
            "ip_packet": {
                "version": self.ip_version,
                "header_length": self.header_len,
                "header_total_length": self.total_len,
                "time_to_live": self.TTL,
                "protocol": self.ip_proto,
                "destination_ip": self.destination_ip,
                "source_ip": self.source_ip,
                "tcp_segment": {
                    "destination_port": self.destination_port,
                    "source_port": self.source_port,
                    "header_length": self.header_length,
                },
            },
        }

#!/usr/bin/env python3

"""
Command line interface

Bogdan Lozhkin
"""

import argparse
import logging
import sys

from blomo import __version__

from blomo.classes import EtherFrame
import blomo.network_utils as net_utils


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
LOG = logging.getLogger(__name__)

TAB1 = "\t"
TAB2 = "\t\t"
TAB3 = "\t\t\t"


def blomo(vip_intf, vip_targets, vip_ip, vip_port):
    """Entry point for running the script."""
    LOG.info(
        f"Using Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} to run program"
    )
    LOG.info("Running BLOMO Load Balancer Server")

    # Handle empty arguments with default values
    vip_ip = vip_ip if vip_ip is not None else "127.0.0.1"
    vip_port = vip_port if vip_port is not None else "80"

    # Check if vip_intf is valid interface
    if (
        len([intf for intf in net_utils.get_local_interfaces() if vip_intf in intf])
        == 0
    ):
        LOG.error(f"{vip_intf} was not found as a valid interface in the Network")
        return

    LOG.info("======= CONFIGURATION =======")
    LOG.info(f"Load Balancer interfaces: {net_utils.get_local_interfaces()}")
    LOG.info(f"VIP interface: {vip_intf}")
    LOG.info(f"VIP IP: {vip_ip}")
    LOG.info(f"VIP Port: {vip_port}")
    LOG.info(f"VIP MAC Address: {net_utils.get_mac_addr(vip_intf)}")
    LOG.info(f"Target IP list: {vip_targets}")
    LOG.info("Target MAC list: ['00:0C:29:98:EE:A9']")
    LOG.info("=============================")
    LOG.info("Starting BLOMO Server...\n")

    # Create Raw socket binded to passed Interface
    s = net_utils.create_raw_socket(vip_intf)

    # Listen on the raw socket
    while True:
        raw_data, addr = s.recvfrom(65565)
        dest_mac, src_mac, eth_type, ether_data = net_utils.ethernet_unpack(raw_data)

        # Isolate only Frames that matter (destination is Virtual Mac address and EtherType is IPv4)
        if (
            dest_mac == net_utils.get_mac_addr(vip_intf)
            and eth_type == net_utils.EtherType.IPV4.value
        ):
            # IP Packat found, unpacking it
            (
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
                source_ip,
                destination_ip,
                ip_data,
            ) = net_utils.ipv4_unpack(ether_data)
            if ip_proto == net_utils.IpProto.TCP.value:
                (
                    source_port,
                    destination_port,
                    sequence_number,
                    ack_number,
                    header_length,
                    window_size,
                    chucksum,
                    urgent_pointer,
                    tcp_data,
                ) = net_utils.tcp_unpack(ip_data)
                # Display Frame->Packet->Segment
                ether_frame = EtherFrame(
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
                )
                show_ether_frame(ether_frame.to_dict())

        if eth_type == net_utils.EtherType.ARP.value:
            LOG.warning("ARP Packat found, following actions will be executed :")
            LOG.info("Check if the ARP request is sent to the Virtual IP address")
            LOG.info(
                "If yes, generate a raw Ethernet ARP reply and transmit it back to the requester using the fake MAC address (00:11:11:....) owned by the load balancer."
            )
            LOG.info(
                "The requester will learn this Virtual IP <-> Virtual MAC address pairing."
            )
            LOG.info("====================================\n")


def show_ether_frame(ether_frame: EtherFrame):
    LOG.info("========== ETHERNET FRAME ==========")
    LOG.info(f"Destination Mac : {ether_frame['destination_mac']}")
    LOG.info(f"Source Mac : {ether_frame['source_mac']}")
    LOG.info(f"EtherType : {ether_frame['ethernet_type']}")
    LOG.info("=======  IPv4 Packet   =======")
    LOG.info(f"Version : {ether_frame['ip_packet']['version']}")
    LOG.info(f"Header Length : {ether_frame['ip_packet']['header_length']} Bytes")
    LOG.info(f"Total Length : {ether_frame['ip_packet']['header_total_length']}")
    LOG.info(f"Time To Live : {ether_frame['ip_packet']['time_to_live']}")
    LOG.info(f"Protocol : {ether_frame['ip_packet']['protocol']}")
    LOG.info(f"Destination IP : {ether_frame['ip_packet']['destination_ip']}")
    LOG.info(f"Source IP : {ether_frame['ip_packet']['source_ip']}")
    LOG.info("====  TCP Segment   ====")
    LOG.info(
        f"Destination Port : {ether_frame['ip_packet']['tcp_segment']['destination_port']}"
    )
    LOG.info(f"Source Port : {ether_frame['ip_packet']['tcp_segment']['source_port']}")
    LOG.info(
        f"Header Length : {ether_frame['ip_packet']['tcp_segment']['header_length']} Bytes"
    )
    LOG.info("====================================\n")


def get_parser():
    parser = argparse.ArgumentParser(prog="blomo", description="HTTP Load Balancer.")
    parser.add_argument(
        "--version",
        action="version",
        version=f"blomo v{__version__}",
        help="show %(prog)s's version number and exit",
    )
    parser.add_argument(
        "--intf", metavar="VIP_INTERFACE", help="VIP interface (e.g. eth0)"
    )
    parser.add_argument("--port", metavar="VIP_PORT", help="VIP port number (e.g. 80)")
    parser.add_argument(
        "--ip", metavar="VIP_IP", help="VIP IP address (e.g. 192.168.0.100)"
    )
    parser.add_argument(
        "--targets",
        metavar="TARGETS",
        help="Comma separated list of HTTP servers for proxy to target (hostname or IP)",
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    blomo(args.intf, args.targets, vip_ip=args.ip, vip_port=args.port)


if __name__ == "__main__":
    main()

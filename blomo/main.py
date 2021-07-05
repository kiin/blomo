#!/usr/bin/env python3

import argparse
import logging
import sys

from blomo import __version__

from blomo.classes import Frame, Packet, Segment
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
        ethernet_frame = Frame(*net_utils.ethernet_unpack(raw_data))

        # Isolate only Frames that matter (destination is Virtual Mac address and EtherType is IPv4)
        if (
            ethernet_frame.destination_mac_address == net_utils.get_mac_addr(vip_intf)
            and ethernet_frame.type == net_utils.EtherType.IPV4.value
        ):
            # IP Packat found, unpacking it
            ipv4_packet = Packet(*net_utils.ipv4_unpack(ethernet_frame.raw_data))

            if ipv4_packet.ip_proto == net_utils.IpProto.TCP.value:
                tcp_segment = Segment(*net_utils.tcp_unpack(ipv4_packet.raw_data))
                show_full_packet(
                    ethernet_frame.to_dict(),
                    ipv4_packet.to_dict(),
                    tcp_segment.to_dict(),
                )

        if ethernet_frame.type == net_utils.EtherType.ARP.value:
            """
            LOG.warning("ARP Packat found, following actions will be executed :")
            LOG.info("Check if the ARP request is sent to the Virtual IP address")
            LOG.info(
                "If yes, generate a raw Ethernet ARP reply and transmit it back to the requester using the fake MAC address (00:11:11:....) owned by the load balancer."
            )
            LOG.info(
                "The requester will learn this Virtual IP <-> Virtual MAC address pairing."
            )
            LOG.info("====================================\n")
            """

def show_full_packet(frame: Frame, packet: Packet, segment: Segment):
    # Display Frame->Packet->Segment
    LOG.info("========== ETHERNET FRAME ==========")
    LOG.info(f"Destination Mac : {frame['destination_mac']}")
    LOG.info(f"Source Mac : {frame['source_mac']}")
    LOG.info(f"EtherType : {frame['ethernet_type']}")
    LOG.info("=======  IPv4 Packet   =======")
    LOG.info(f"Version : {packet['version']}")
    LOG.info(f"Header Length : {packet['header_length']} Bytes")
    LOG.info(f"Total Length : {packet['header_total_length']}")
    LOG.info(f"Time To Live : {packet['time_to_live']}")
    LOG.info(f"Protocol : {packet['protocol']}")
    LOG.info(f"Destination IP : {packet['destination_ip']}")
    LOG.info(f"Source IP : {packet['source_ip']}")
    LOG.info("====  TCP Segment   ====")
    LOG.info(f"Destination Port : {segment['destination_port']}")
    LOG.info(f"Source Port : {segment['source_port']}")
    LOG.info(f"Header Length : {segment['header_length']} Bytes")
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

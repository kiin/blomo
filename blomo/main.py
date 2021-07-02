#!/usr/bin/env python3

"""
Command line interface

Bogdan Lozhkin
"""

import argparse
import logging
import sys

from blomo import __version__
from blomo.network_utils import get_local_interfaces, get_mac_addr, create_raw_socket


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
LOG = logging.getLogger(__name__)

def blomo(vip_intf, vip_targets, vip_ip, vip_port):
    """Entry point for running the script."""
    LOG.info(f"Using Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} to run program")
    LOG.info("Running BLOMO Load Balancer Server")

    # Handle empty arguments with default values
    vip_ip = vip_ip if vip_ip != None else "127.0.0.1"
    vip_port = vip_port if vip_port != None else "80"

    # Check if vip_intf is valid interface
    if len([intf for intf in get_local_interfaces() if vip_intf in intf]) == 0:
        LOG.error(f"{vip_intf} was not found as a valid interface in the Network")
        return

    LOG.info("======= CONFIGURATION =======")
    LOG.info(f"Load Balancer interfaces: {get_local_interfaces()}")
    LOG.info(f"VIP interface: {vip_intf}")
    LOG.info(f"VIP IP: {vip_ip}")
    LOG.info(f"VIP Port: {vip_port}")
    LOG.info(f"VIP MAC Address: {get_mac_addr(vip_intf)}")
    LOG.info(f"Target IP list: {vip_targets}")
    LOG.info(f"Target MAC list: ['00:0C:29:98:EE:A9']")
    LOG.info("=============================")
    LOG.info("Starting BLOMO Server")

    # Create Raw socket binded to passed Interface
    s = create_raw_socket(vip_intf)
    s.listen(1)

def get_parser():
    parser = argparse.ArgumentParser(prog="blomo", description="HTTP Load Balancer.")

    parser.add_argument("--version", action="version", version=f"blomo v{__version__}", help="show %(prog)s\'s version number and exit")
    parser.add_argument("--intf", metavar="VIP_INTERFACE", help="VIP interface (e.g. eth0)")
    parser.add_argument("--port", metavar="VIP_PORT", help="VIP port number (e.g. 80)")
    parser.add_argument("--ip", metavar="VIP_IP", help="VIP IP address (e.g. 192.168.0.100)")
    parser.add_argument("--targets", metavar="TARGETS", help="Comma separated list of HTTP servers for proxy to target (hostname or IP)")

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    blomo(args.intf, args.targets, vip_ip=args.ip, vip_port=args.port)


if __name__ == "__main__":
    main()
import argparse
import logging

from blomo import __version__


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
LOG = logging.getLogger(__name__)


def blomo():
    """Entry point for running the script."""
    LOG.info("Starting clinker")

def get_parser():
    parser = argparse.ArgumentParser(prog='blomo', description='HTTP Load Balancer.')

    parser.add_argument("--version", action='version', version=f'blomo v{__version__}', help='show %(prog)s\'s version number and exit')
    parser.add_argument('--intf', metavar='VIP_INTERFACE', help='VIP interface (e.g. eth0)')

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    blomo()


if __name__ == "__main__":
    main()
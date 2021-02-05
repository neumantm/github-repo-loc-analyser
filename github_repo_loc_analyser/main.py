#!/usr/bin/env python3

from . import setup
from .master import Master


def main():
    """Run the program as master."""
    setup()
    master = Master()
    master.start()


if __name__ == "__main__":
    main()

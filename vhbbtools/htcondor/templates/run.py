#!/usr/bin/env python
import logging
import sys

from vhbbtools.utils import load_pkl


def main():
    # Create a logger in case the job utilizes the logging module.
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%a %b %d %H:%M:%S %Z %Y',
        level=logging.DEBUG,
    )
    logger = logging.getLogger(__file__)
    # Deserialize and call the job.
    job = load_pkl(sys.argv[1])
    job()


if __name__ == '__main__':

    status = main()
    sys.exit(status)


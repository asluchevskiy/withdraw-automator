# -*- coding: utf-8 -*-
import csv
from app.withdrawer import Withdrawer
from web3pylib import load_lines, setup_color_logging, setup_file_logging
import config
import logging


def main():
    wallets = [l.split(',') for l in load_lines(config.WALLETS_FILE)]
    w = Withdrawer(networks=config.NETWORKS)
    setup_color_logging(w.logger)
    setup_file_logging(w.logger, config.LOG_FILE)
    w.run(wallets=wallets)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    main()

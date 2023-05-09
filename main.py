# -*- coding: utf-8 -*-
import csv
from app.withdrawer import Withdrawer
from web3pylib import load_lines, setup_color_logging, setup_file_logging
import config
import logging


def main():
    with open(config.WALLETS_FILE) as f:
        reader = csv.DictReader(f)
        wallets = [row for row in reader]
    w = Withdrawer(networks=config.NETWORKS, delay_interval=config.NEXT_WALLET_DELAY)
    setup_color_logging(w.logger)
    setup_file_logging(w.logger, config.LOG_FILE)
    w.run(wallets=wallets)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    main()

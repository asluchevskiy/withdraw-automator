# -*- coding: utf-8 -*-
import csv
from app.withdrawer import Withdrawer
from app.utils import load_lines, setup_color_logging, setup_file_logging
from app.enums import Mode
import config
import logging


def main():
    with open(config.WALLETS_FILE) as f:
        reader = csv.DictReader(f)
        wallets = [row for row in reader]
    w = Withdrawer(networks=config.NETWORKS, delay_interval=config.NEXT_WALLET_DELAY)
    setup_color_logging(w.logger)
    setup_file_logging(w.logger, config.LOG_FILE)
    if config.MODE == Mode.PERCENT:
        amount_range = config.WITHDRAW_PERCENT
    elif config.MODE == Mode.AMOUNT:
        amount_range = config.WITHDRAW_AMOUNT
    elif config.MODE == Mode.KEEP:
        amount_range = config.WITHDRAW_AMOUNT_KEEP
    else:
        amount_range = None
    w.run(wallets=wallets, token_address=config.TOKEN_CONTRACT, mode=config.MODE, amount_range=amount_range)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    main()

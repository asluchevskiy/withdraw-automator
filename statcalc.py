# -*- coding: utf-8 -*-
import logging

from web3pylib import load_lines, setup_color_logging, setup_file_logging

import config
from app.statcalc import StatCalculator


def main():
    # logging
    logger = logging.getLogger('stat')
    setup_color_logging(logger)
    setup_file_logging(logger, config.LOG_FILE)
    # get wallets
    wallets = load_lines(config.STAT_WALLETS_FILE)
    # run stat calculator
    s = StatCalculator(network=config.NETWORKS['arbitrum nova'])
    res = s.run(wallets)
    # save result data
    s.save(res, config.STAT_WALLETS_RESULT_FILE)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    main()

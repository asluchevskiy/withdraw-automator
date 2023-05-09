# -*- coding: utf-8 -*-
NETWORKS = {
    'ethereum': {
        'rpc': '',
        'explorer': '',
    },
    'polygon': {
        'rpc': '',
        'explorer': '',
    },
    'binance': {
        'rpc': '',
        'explorer': '',
    },
    'avalanche': {
        'rpc': '',
        'explorer': '',
    }
}

WALLETS_FILE = 'wallets.csv'
LOG_FILE = 'default.log'

NEXT_WALLET_DELAY = (30, 60)

try:
    from local_config import *
except ImportError:
    pass

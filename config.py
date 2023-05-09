# -*- coding: utf-8 -*-
NETWORKS = {
    'ethereum': {
        'rpc': 'https://eth.llamarpc.com',
        'explorer': 'https://etherscan.io',
    },
    'polygon': {
        'rpc': 'https://rpc-mainnet.maticvigil.com',
        'explorer': 'https://polygonscan.com/',
    },
    'binance': {
        'rpc': 'https://bsc-dataseed.binance.org',
        'explorer': 'https://bscscan.com',
    },
    'avalanche': {
        'rpc': 'https://api.avax.network/ext/bc/C/rpc',
        'explorer': 'https://snowtrace.io',
    },
    'fantom': {
        'rpc': 'https://rpcapi.fantom.network',
        'explorer': 'https://ftmscan.com',
    },
    'arbitrum one': {
        'rpc': 'https://arb1.arbitrum.io/rpc',
        'explorer': 'https://arbiscan.io',
    },
    'arbitrum nova': {
        'rpc': 'https://nova.arbitrum.io/rpc',
        'explorer': 'https://nova.arbiscan.io',
    },
    'optimism': {
        'rpc': 'https://mainnet.optimism.io',
        'explorer': 'https://optimistic.etherscan.io',
    }
}

WALLETS_FILE = 'wallets.csv'
LOG_FILE = 'default.log'

NEXT_WALLET_DELAY = (30, 60)

try:
    from local_config import *
except ImportError:
    pass

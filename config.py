# -*- coding: utf-8 -*-
from app.enums import Mode

NETWORKS = {
    'ethereum': {
        'rpc': 'https://eth.llamarpc.com',
        'explorer': 'https://etherscan.io',
    },
    'polygon': {
        'rpc': 'https://polygon.llamarpc.com',
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

TOKEN_CONTRACT = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'  # Token Contract or empty string for native token
# TOKEN_CONTRACT = None

WITHDRAW_PERCENT = (30, 80)
WITHDRAW_AMOUNT_KEEP = (0.1, 0.1)
WITHDRAW_AMOUNT = (1, 1.5)
MODE = Mode.ALL  # Model.ALL | Mode.PERCENT | Mode.KEEP | Mode.AMOUNT -- working mode

STAT_WALLETS_FILE = 'wallets.txt'
STAT_WALLETS_RESULT_FILE = 'wallets_stat.csv'

try:
    from local_config import *
except ImportError:
    pass

# -*- coding: utf-8 -*-
import logging
from web3.eth import Eth
from web3pylib import Node, Account


class Withdrawer:
    def __init__(self, networks):
        self.logger = logging.getLogger('withdrawer')
        self.logger.setLevel(level=logging.DEBUG)
        self.nodes = {}
        for network in networks:
            if networks[network]['rpc'] and networks[network]['explorer']:
                self.nodes[network] = Node(rpc_url=networks[network]['rpc'],
                                           explorer_url=networks[network]['explorer'])

    def run(self, wallets):
        for private_key, address in wallets:
            pass

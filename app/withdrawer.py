# -*- coding: utf-8 -*-
import requests
import logging
import time
import random
from web3 import Web3
from web3pylib import Node, Account


class Withdrawer:
    def __init__(self, networks, delay_interval):
        self.logger = logging.getLogger('withdrawer')
        self.logger.setLevel(level=logging.DEBUG)
        self.nodes = {}
        self.delay_interval = delay_interval
        self.chains = {c['chainId']: c for c in requests.get('https://chainid.network/chains.json').json()}
        for network_name, network_data in networks.items():
            if network_data['rpc'] and network_data['explorer']:
                self.nodes[network_name] = Node(rpc_url=network_data['rpc'],
                                                explorer_url=network_data['explorer'])

    def delay(self, timeout):
        self.logger.debug(f'delay for {timeout} sec.')
        time.sleep(timeout)

    def random_delay(self, min_max: tuple):
        self.delay(random.randint(min_max[0], min_max[1]))

    def get_transaction_price(self, tx):
        if 'maxFeePerGas' in tx and 'maxPriorityFeePerGas' in tx:
            return tx['gas'] * (tx['maxFeePerGas'] + tx['maxPriorityFeePerGas'])
        else:
            return tx['gas'] * tx['gasPrice']

    def run(self, wallets):
        for i, row in enumerate(wallets):
            is_first = True
            allowed_networks = [n.strip().lower() for n in row['networks'].split(',')]
            if row['private_key'].startswith('#'):
                continue
            for network_name, node in self.nodes.items():
                if row['networks'] and network_name not in allowed_networks:
                    continue
                symbol = self.chains[node.chan_id]['nativeCurrency']['symbol']
                acc = Account(node=node, private_key=row['private_key'])
                if is_first:
                    self.logger.info(acc.address)
                    is_first = False
                balance = acc.balance_in_wei
                if not balance or balance < Web3.to_wei(0.0001, 'ether'):
                    continue
                self.logger.debug(f'balance {Web3.from_wei(balance, "ether")} {symbol} in {network_name.title()} '
                                  f'(chain_id={node.chan_id}): '
                                  f'{node.get_explorer_address_url(acc.address)}')
                try:
                    tx = acc.estimate_transfer_gas(row['to_address'], Web3.to_wei(0.0001, 'ether'))
                    tx['value'] = balance - self.get_transaction_price(tx)
                    signed_tx = acc.sign_transaction(tx)
                    tx_hash = node.send_raw_transaction(signed_tx.rawTransaction)
                    self.logger.debug(f'sent {Web3.from_wei(tx["value"], "ether")} {symbol}: '
                                      f'{node.get_explorer_transaction_url(tx_hash)}')
                    tx_receipt = node.web3.eth.wait_for_transaction_receipt(tx_hash)
                except Exception as ex:
                    self.logger.error(ex)
                    continue
            if i+1 < len(wallets):
                self.random_delay(self.delay_interval)

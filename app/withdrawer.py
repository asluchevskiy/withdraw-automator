# -*- coding: utf-8 -*-
import requests
import logging
import time
import random
from web3 import Web3
from app.api import Node, Account, Erc20Token
from app.utils import random_float
from app.enums import Mode


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
                                                explorer_url=network_data['explorer'], network_name=network_name)

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

    def process_withdraw(self, account: Account, to_address, token_address, mode, amount_range):
        balance = account.balance_in_wei
        node = account.node
        network_symbol = self.chains[node.chain_id]['nativeCurrency']['symbol']
        # logging
        self.logger.debug(f'balance {Web3.from_wei(balance, "ether")} {network_symbol} in {node.network_name.title()} '
                          f'(chain_id={node.chain_id}): '
                          f'{node.get_explorer_address_url(account.address)}')
        if not balance or balance < Web3.to_wei(0.00001, 'ether'):
            raise ValueError('too low balance to transfer')
        tx = account.estimate_transfer_gas(to_address, Web3.to_wei(0.00001, 'ether'))
        transaction_fee = self.get_transaction_price(tx)
        if token_address:
            token = Erc20Token(node=node, address=token_address)
            total_balance = token.balance_of(account.address)
            symbol = token.symbol
            self.logger.debug(f'token balance {token.native_to_amount(total_balance)} {symbol}')
            if not total_balance:
                return
        else:
            token = None
            total_balance = balance - transaction_fee
            symbol = network_symbol
        if mode == mode.PERCENT:
            random_percent = random_float(*amount_range)
            transfer_amount = int(total_balance * random_percent / 100)
        elif mode == mode.AMOUNT:
            if token_address:
                transfer_amount = token.amount_to_native(random_float(*amount_range))
            else:
                transfer_amount = Web3.to_wei(random_float(*amount_range), 'ether')
        elif mode == mode.KEEP:
            if token_address:
                transfer_amount = total_balance - token.amount_to_native(random_float(*amount_range))
            else:
                transfer_amount = total_balance - Web3.to_wei(random_float(*amount_range), 'ether')
        else:
            transfer_amount = total_balance
        # checks
        if transfer_amount < 0:
            raise ValueError('transfer_amount < 0 (because of transfer fee)')
        elif token_address and transfer_amount > total_balance:
            raise ValueError('transfer_amount > total_balance')
        elif not token_address and transfer_amount + transaction_fee > balance:
            raise ValueError('transfer_amount + transaction_fee > balance')

        # transferring
        if not token_address:
            tx['value'] = transfer_amount
            signed_tx = account.sign_transaction(tx)
            tx_hash = node.send_raw_transaction(signed_tx.rawTransaction)
            self.logger.debug(f'sent {Web3.from_wei(tx["value"], "ether")} {symbol}: {node.get_explorer_transaction_url(tx_hash)}')
            tx_receipt = node.web3.eth.wait_for_transaction_receipt(tx_hash)
        else:
            tx_hash = token.transfer(account=account, to_address=to_address, amount=transfer_amount)
            self.logger.debug(
                f'sent {token.native_to_amount(transfer_amount)} {symbol}: {node.get_explorer_transaction_url(tx_hash)}')
            tx_receipt = node.web3.eth.wait_for_transaction_receipt(tx_hash)

    def run(self, wallets, token_address=None, mode=Mode.ALL, amount_range=None):
        for i, row in enumerate(wallets):
            is_first_network = True
            allowed_networks = [n.strip().lower() for n in row['networks'].split(',')]
            if row['private_key'].startswith('#'):
                continue
            for network_name, node in self.nodes.items():
                if row['networks'] and network_name not in allowed_networks:
                    continue
                account = Account(node=node, private_key=row['private_key'])
                if is_first_network:
                    self.logger.info(account.address)
                    is_first_network = False
                try:
                    self.process_withdraw(account, row['to_address'], token_address, mode, amount_range)
                except Exception as ex:
                    self.logger.error(ex)
            if i+1 < len(wallets):
                self.random_delay(self.delay_interval)

# -*- coding: utf-8 -*-
import json
import random
import time
from functools import cached_property
from web3 import Web3
from web3_proxy_providers import HttpWithProxyProvider


class Node:
    def __init__(self, rpc_url: str, weth_address: str = '0x0000000000000000000000000000000000000000',
                 explorer_url: str = None, proxy: str = None, network_name: str = None):
        if proxy:
            try:
                proxy_host, proxy_port, proxy_user, proxy_password = proxy.split(':')
            except ValueError:
                raise Exception('bad proxy line format: %s' % proxy)
            proxy_url = f'http://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}'
            http_provider = HttpWithProxyProvider(endpoint_uri=rpc_url, proxy_url=proxy_url)
        else:
            http_provider = Web3.HTTPProvider(endpoint_uri=rpc_url)
        self._web3 = Web3(http_provider)
        self.weth_address = Web3.to_checksum_address(weth_address)
        if not explorer_url.endswith('/'):
            explorer_url += '/'
        self.explorer_url = explorer_url
        # self.max_fee_per_gas = self._web3.to_wei('0.1', 'gwei')
        # self.max_priority_fee_per_gas = self._web3.to_wei('0.1', 'gwei')
        self.network_name = network_name

    @property
    def web3(self):
        return self._web3

    @property
    def block_number(self):
        return self._web3.eth.block_number

    @property
    def gas_price(self):
        return self._web3.eth.gas_price

    @property
    def max_priority_fee(self):
        return self._web3.eth.max_priority_fee

    @property
    def max_fee(self):
        return self.gas_price + self.max_priority_fee

    @cached_property
    def chain_id(self):
        return self._web3.eth.chain_id

    def get_block(self, block_number):
        return self._web3.eth.get_block(block_number)

    def get_transaction(self, tx_hash):
        return self._web3.eth.get_transaction(tx_hash)

    def get_transaction_count(self, address):
        return self._web3.eth.get_transaction_count(address)

    def get_balance(self, address):
        balance_in_wei = self._web3.eth.get_balance(address)
        return Web3.from_wei(balance_in_wei, 'ether')

    def send_raw_transaction(self, raw_transaction):
        tx_hash = self._web3.eth.send_raw_transaction(raw_transaction)
        return tx_hash

    def estimate_gas(self, tx, randomize=True):
        gas = self._web3.eth.estimate_gas(tx)
        if randomize:
            gas = int(gas * 1.25) + random.randint(1, 1000)
        return gas

    def check_in_transaction(self, from_address, to_address, from_block, to_block=None, amount=None):
        if not to_block:
            to_block = self.block_number
        for block_num in range(from_block, to_block + 1):
            block = self.get_block(block_num)
            for tx_hash in block['transactions']:
                tx = self.web3.eth.get_transaction(tx_hash)
                if tx and tx['from'] == from_address and tx['to'] == to_address:
                    if amount and amount != tx['value']:
                        continue
                    return tx
        return None

    def wait_in_transaction(self, from_address, to_address, from_block, amount=None, timeout=60):
        start_time = time.time()
        _from_block = from_block
        while True:
            last_block = self.block_number
            if last_block > _from_block:
                # print(f'checking from {_from_block} to {last_block}')
                res = self.check_in_transaction(from_address, to_address, _from_block, last_block, amount)
                if res:
                    return res
                _from_block = last_block + 1
            time.sleep(3)
            if time.time() - start_time > timeout:
                return False

    def get_explorer_transaction_url(self, tx_hash):
        return f'{self.explorer_url}tx/{self._web3.to_hex(tx_hash)}'

    def get_explorer_address_url(self, address):
        return f'{self.explorer_url}address/{address}'


class Account:
    def __init__(self, node: Node, private_key: str):
        self._node = node
        self._web3 = node.web3
        self._account = self._web3.eth.account.from_key(private_key)
        self._private_key = private_key
        self.address = Web3.to_checksum_address(self._account.address)

    @property
    def balance(self):
        return Web3.from_wei(self.balance_in_wei, 'ether')

    @property
    def node(self):
        return self._node

    @property
    def balance_in_wei(self):
        return self._web3.eth.get_balance(self.address)

    @property
    def transaction_count(self):
        return self._web3.eth.get_transaction_count(self.address)

    def estimate_transfer_gas(self, to_address, amount) -> dict:
        chain_id = self._web3.eth.chain_id
        tx = {
            'chainId': chain_id,
            'from': self.address,
            'to': Web3.to_checksum_address(to_address),
            'value': amount,
            'nonce': self.transaction_count,
        }
        if chain_id in (324, 250, 56):  # for zksync era, fantom, bsc
            tx.update({
                'gasPrice': self._web3.eth.gas_price,
            })
        else:
            tx.update({
                'maxFeePerGas': int(self._node.max_fee),
                'maxPriorityFeePerGas': self._node.max_priority_fee,
            })
        # print(tx['maxFeePerGas'], tx['maxPriorityFeePerGas'])
        if chain_id in (42161, ):  # gas fix (arbitrum one)
            tx['maxFeePerGas'] = int(tx['maxFeePerGas'] * 1.25)
        tx['gas'] = self._web3.eth.estimate_gas(tx)
        return tx

    def transfer(self, to_address, amount):
        tx = self.estimate_transfer_gas(to_address, amount)
        signed_tx = self.sign_transaction(tx)
        return self._node.send_raw_transaction(signed_tx.rawTransaction)

    def sign_transaction(self, transaction):
        signed_tx = self._web3.eth.account.sign_transaction(transaction, private_key=self._private_key)
        return signed_tx

    def build_transaction(self, tx, amount):
        tx_data = {
            'value': amount,
            'from': self.address,
            'nonce': self.transaction_count,
        }
        if self._web3.eth.chain_id in (324, 250, 56):  # for zksync era, fantom, bsc
            tx_data.update({
                'gasPrice': self._web3.eth.gas_price,
            })
        else:
            tx_data.update({
                'maxFeePerGas': int(self._node.max_fee),
                'maxPriorityFeePerGas': self._node.max_priority_fee,
            })
        tx = tx.build_transaction(tx_data)
        tx['gas'] = self._node.estimate_gas(tx)
        return tx


class Contract:

    def __init__(self, node: Node, name: str, address: str, abi: dict = None):
        if not abi:
            with open(f'abi/{name}.json') as f:
                self.abi = json.load(f)
        else:
            self.abi = abi
        self.address = Web3.to_checksum_address(address)
        self.name = name
        self._node = node
        self._web3 = node.web3
        self._contract = self._web3.eth.contract(address=self.address, abi=self.abi)

    @property
    def functions(self):
        return self._contract.functions


class Erc20Token(Contract):
    def __init__(self, node, address):
        super().__init__(node, 'erc20', address)

    def balance_of(self, address: str, native: bool = True):
        balance = self.functions.balanceOf(Web3.to_checksum_address(address)).call()
        if not native:
            balance = balance / 10 ** self.decimals
        return balance

    def allowance(self, address: str, contract_address: str, native: bool = True):
        allowance = self.functions.allowance(address, contract_address).call()
        if not native:
            allowance = allowance / 10 ** self.decimals
        return allowance

    def amount_to_native(self, amount):
        return int(amount * 10 ** self.decimals)

    def native_to_amount(self, native_amount):
        return native_amount / 10 ** self.decimals

    def approve(self, account: Account, contract_address: str, amount: int = None):
        if not amount:
            amount = self._web3.to_wei(2 ** 64 - 1, 'ether')
        tx = self.functions.approve(contract_address, amount)
        tx = account.build_transaction(tx, 0)
        signed_tx = account.sign_transaction(tx)
        return self._node.send_raw_transaction(signed_tx.rawTransaction)

    def transfer(self, account: Account, to_address: str, amount: int):
        tx = self.functions.transfer(to_address, amount)
        tx = account.build_transaction(tx, 0)
        signed_tx = account.sign_transaction(tx)
        return self._node.send_raw_transaction(signed_tx.rawTransaction)

    @cached_property
    def decimals(self):
        return self.functions.decimals().call()

    @cached_property
    def symbol(self):
        return self.functions.symbol().call()


class UniswapV2Exchange(Contract):
    def __init__(self, node, name, address, abi=None):
        super().__init__(node, name, address, abi=abi)

    def swap_eth_to_token(self, account: Account, amount: float, token: Erc20Token, slippage_percent: int = 1):
        deadline = self._node.get_block('latest').timestamp + 60 * 10  # 10 minutes
        amount_in, amount_out = self.functions.getAmountsOut(self._web3.to_wei(amount, 'ether'),
                                                             [self._node.weth_address, token.address]).call()
        tx = self.functions.swapExactETHForTokens(
            int(amount_out * (1.0 - slippage_percent / 100.0)),  # slippage 1%
            [self._node.weth_address, token.address],  # from token, to token
            account.address,  # receiver
            deadline  # deadline
        )
        tx = account.build_transaction(tx, amount_in)
        signed_tx = account.sign_transaction(tx)
        return self._node.send_raw_transaction(signed_tx.rawTransaction)

    def swap_token_to_eth(self, account: Account, amount: int, token: Erc20Token, slippage_percent: int = 1):
        deadline = self._node.get_block('latest').timestamp + 60 * 10  # 10 minutes
        amount_in, amount_out = self.functions.getAmountsOut(amount,
                                                             [token.address, self._node.weth_address]).call()
        tx = self.functions.swapExactTokensForETH(
            amount_in,
            int(amount_out * (1.0 - slippage_percent / 100.0)),  # slippage 1%
            [token.address, self._node.weth_address],
            account.address,
            deadline
        )
        tx = account.build_transaction(tx, 0)
        signed_tx = account.sign_transaction(tx)
        return self._node.send_raw_transaction(signed_tx.rawTransaction)

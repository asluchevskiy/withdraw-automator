# -*- coding: utf-8 -*-
import csv
import logging
import random
import time
from typing import Union

import requests
from web3pylib.api import Node


class BaseTransactionMatch:

    def __init__(self):
        pass

    @staticmethod
    def match(tx):
        raise NotImplementedError


class BridgeDepositMatch(BaseTransactionMatch):
    name = 'bridge_deposit'

    @staticmethod
    def match(tx):
        if int(tx['txreceipt_status']) and int(tx['gasUsed']) == 0:
            return 1
        return 0


class BridgeWithdrawMatch(BaseTransactionMatch):
    name = 'bridge_withdraw'

    @staticmethod
    def match(tx):
        if not int(tx['txreceipt_status']):
            return 0
        if tx['to'] == '0x0000000000000000000000000000000000000064' and tx['functionName'].startswith('withdrawEth'):
            return 1
        return 0


class OrbiterBaseMatch(BaseTransactionMatch):
    orbiter_addresses = (
        '0x80C67432656d59144cEFf962E8fAF8926599bCF8'.lower(),
        '0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8'.lower()
    )


class OrbiterDepositMatch(OrbiterBaseMatch):
    name = 'orbiter_deposit'

    @staticmethod
    def match(tx):
        if not int(tx['txreceipt_status']):
            return 0
        if tx['from'] in OrbiterBaseMatch.orbiter_addresses:
            return 1
        return 0


class OrbiterWithdrawMatch(BaseTransactionMatch):
    name = 'orbiter_withdraw'

    @staticmethod
    def match(tx):
        if not int(tx['txreceipt_status']):
            return 0
        if tx['to'] in OrbiterBaseMatch.orbiter_addresses:
            return 1
        return 0


class StatCalculator:
    def __init__(self, network: dict):
        self.logger = logging.getLogger('stat')
        self.logger.setLevel(level=logging.DEBUG)
        self.node = Node(rpc_url=network['rpc'], explorer_url=network['explorer'])

    def get_tx_data(self, address):
        api_url = f'https://api-nova.arbiscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999'
        res = requests.get(api_url)
        tx_data = res.json()
        if tx_data['message'] != 'OK':
            raise RuntimeError(f'could not get TX data for {address}')
        # tx_data = json.load(open('../_temp/api.json'))
        return tx_data

    def delay(self, timeout):
        self.logger.debug(f'delay for {timeout} sec.')
        time.sleep(timeout)

    def random_delay(self, min_max: tuple):
        self.delay(random.randint(min_max[0], min_max[1]))

    def run(self, addresses: Union[list, tuple]):
        tx_checks = (BridgeDepositMatch, BridgeWithdrawMatch, OrbiterDepositMatch, OrbiterWithdrawMatch)
        data = []
        for address in addresses:
            result = {check.name: 0 for check in tx_checks}
            result['address'] = address
            self.logger.info(address)
            self.logger.debug(self.node.get_explorer_address_url(address))
            tx_data = self.get_tx_data(address)
            for tx in tx_data['result']:
                for check in tx_checks:
                    result[check.name] += check.match(tx)
            data.append(result)
            self.delay(5)
        return data

    def save(self, data, filename):
        self.logger.info(f'Saving to {filename}')

        if not data:
            return

        with open(filename, 'w') as fw:
            keys = sorted(data[0].keys())
            keys.remove('address')
            keys.insert(0, 'address')
            writer = csv.DictWriter(fieldnames=keys, f=fw)
            writer.writeheader()
            for item in data:
                writer.writerow(item)


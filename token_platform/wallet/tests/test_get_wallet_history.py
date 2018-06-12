
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from tests.test_utils import BaseTestClass

import pytest
from asynctest import patch
from conf import settings
from router import reverse
from wallet.get_wallet_history import get_wallet_history_from_request


class TestGetWalletHistoryFromRequest(BaseTestClass):

    async def setUpAsync(self):
        self.wallet_address = 'GAM47BTKU5RRA4NAVXO3WNWJ6YGGYIVJ4BK6YGOOY4URZ3VRDRX4N4O5'

    @unittest_run_loop
    async def test_get_wallet_history_from_request_with_minimum_params_success(self):
        params = {
            'type': 'account_created'
        }
        get_wallet_history_url = reverse('wallet-history',wallet_address=self.wallet_address)
        resp = await self.client.request("GET", get_wallet_history_url, params=params)
        assert resp.status == 200

    @unittest_run_loop
    async def test_get_wallet_history_from_request_with_all_params_success(self):
        params = {
            'limit': 20,
            'type': 'signer_created',
            'sort': 'DESC',
            'offset': 'ABCSDSDLK',
            'start-date': '2018-06-12T02:38:34Z',
            'end-date': '2019-06-12T02:38:34Z'
        }
        get_wallet_history_url = reverse('wallet-history',wallet_address=self.wallet_address)
        resp = await self.client.request("GET", get_wallet_history_url, params=params)
        assert resp.status == 200

    @unittest_run_loop
    async def test_get_wallet_history_from_request_fail_date_wrong_format(self):
        params = {
            'limit': 20,
            'type': 'signer_created',
            'sort': 'ASC',
            'offset': 'ABCSDSDLK',
            'start-date': '2018-06-12',
            'end-date': '2019-06-12T02:38:34Z'
        }
        get_wallet_history_url = reverse('wallet-history',wallet_address=self.wallet_address)
        resp = await self.client.request("GET", get_wallet_history_url, params=params)
        assert resp.status == 400

    @unittest_run_loop
    async def test_get_wallet_history_from_request_fail_invalid_sort_value(self):
        params = {
            'limit': 20,
            'type': 'signer_created',
            'sort': 'ASCB',
            'offset': 'ABCSDSDLK',
            'start-date': '2018-06-12T02:38:34Z',
            'end-date': '2019-06-12T02:38:34Z'
        }
        get_wallet_history_url = reverse('wallet-history',wallet_address=self.wallet_address)
        resp = await self.client.request("GET", get_wallet_history_url, params=params)
        assert resp.status == 400

class TestGetWalletHistory(BaseTestClass):

    @unittest_run_loop
    async def test_get_wallet_history_success(self):
        params = {
            'type': 'account_created'
        }
        get_wallet_history_url = reverse('wallet-history',wallet_address=self.wallet_address)
        resp = await self.client.request("GET", get_wallet_history_url, params=params)
        assert resp.status == 200
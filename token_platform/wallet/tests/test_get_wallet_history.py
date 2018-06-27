
from datetime import datetime, timezone, timedelta

import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from tests.test_utils import BaseTestClass

from conf import settings
from router import reverse
from wallet.get_wallet_history import get_wallet_history, format_history


class TestGetWalletHistoryFromRequest(BaseTestClass):

    async def setUpAsync(self):
        self.wallet_address = 'GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE'

    @unittest_run_loop
    @patch('wallet.get_wallet_history.get_wallet_history')
    @patch('wallet.get_wallet_history.format_history')
    async def test_get_wallet_history_from_request_with_minimum_params_success(self, history, format_history):
        format_history.return_value = history.return_value = {
            'status': 200, '@id': 'test-id', 'next': 'test-next', 'previous': 'test-previous'}
        get_wallet_history_url = reverse('wallet-history', wallet_address=self.wallet_address)
        resp = await self.client.request("GET", get_wallet_history_url)
        assert resp.status == 200

    @unittest_run_loop
    @patch('wallet.get_wallet_history.get_wallet_history')
    @patch('wallet.get_wallet_history.format_history')
    async def test_get_wallet_history_from_request_with_all_params_success(self, history, format_history):
        format_history.return_value = history.return_value = {
            'status': 200, '@id': 'test-id', 'next': 'test-next', 'previous': 'test-previous'}
        params = {
            'limit': 20,
            'type': 'signer_created',
            'sort': 'DESC',
            'offset': 'ABCSDSDLK',
            'start-date': '2018-06-12T02:38:34Z',
            'end-date': '2019-06-12T02:38:34Z'
        }
        get_wallet_history_url = reverse('wallet-history', wallet_address=self.wallet_address)
        resp = await self.client.request("GET", get_wallet_history_url, params=params)
        assert resp.status == 200

    @unittest_run_loop
    @patch('wallet.get_wallet_history.get_wallet_history')
    @patch('wallet.get_wallet_history.format_history')
    async def test_get_wallet_history_from_request_fail_date_wrong_format(self, history, format_history):
        format_history.return_value = history.return_value = {
            'status': 200, '@id': 'test-id', 'next': 'test-next', 'previous': 'test-previous'}
        params = {
            'limit': 20,
            'type': 'signer_created',
            'sort': 'ASC',
            'offset': 'ABCSDSDLK',
            'start-date': '2018-06-12',
            'end-date': '2019-06-12T02:38:34Z'
        }
        get_wallet_history_url = reverse('wallet-history', wallet_address=self.wallet_address)
        resp = await self.client.request("GET", get_wallet_history_url, params=params)
        assert resp.status == 400

    @unittest_run_loop
    @patch('wallet.get_wallet_history.get_wallet_history')
    @patch('wallet.get_wallet_history.format_history')
    async def test_get_wallet_history_from_request_fail_invalid_sort_value(self, history, format_history):
        format_history.return_value = history.return_value = {
            'status': 200, '@id': 'test-id', 'next': 'test-next', 'previous': 'test-previous'}
        params = {
            'limit': 20,
            'type': 'signer_created',
            'sort': 'ASCB',
            'offset': 'ABCSDSDLK',
            'start-date': '2018-06-12T02:38:34Z',
            'end-date': '2019-06-12T02:38:34Z'
        }
        get_wallet_history_url = reverse('wallet-history', wallet_address=self.wallet_address)
        resp = await self.client.request("GET", get_wallet_history_url, params=params)
        assert resp.status == 400


class TestGetWalletHistory(BaseTestClass):

    async def setUpAsync(self):
        self.wallet_address = 'GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE'
        self.limit = '1'
        self.offset = '37667833848532999-1'

    @unittest_run_loop
    async def test_get_wallet_history_success(self):

        history = await get_wallet_history(wallet_address=self.wallet_address,
                                           limit=self.limit)

        expect = "_links"
        assert expect in history

    @unittest_run_loop
    async def test_get_wallet_history_with_specific_start_position(self):

        history = await get_wallet_history(wallet_address=self.wallet_address,
                                           limit=self.limit, offset=self.offset)

        expect = "_links"
        assert expect in history


class TestFormatHistory(BaseTestClass):

    async def setUpAsync(self):
        self.wallet_address = 'GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE'
        self.history = {
            "_links": {
                "self": {
                    "href": "https://horizon-testnet.stellar.org/accounts/GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE/effects?cursor=&limit=1&order=asc"
                },
                "next": {
                    "href": "https://horizon-testnet.stellar.org/accounts/GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE/effects?cursor=37667833848532993-1&limit=1&order=asc"
                },
                "prev": {
                    "href": "https://horizon-testnet.stellar.org/accounts/GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE/effects?cursor=37667833848532993-1&limit=1&order=desc"
                }
            },
            "_embedded": {
                "records": [
                    {
                        "_links": {
                            "operation": {
                                "href": "https://horizon-testnet.stellar.org/operations/37667833848532993"
                            },
                            "succeeds": {
                                "href": "https://horizon-testnet.stellar.org/effects?order=desc&cursor=37667833848532993-1"
                            },
                            "precedes": {
                                "href": "https://horizon-testnet.stellar.org/effects?order=asc&cursor=37667833848532993-1"
                            }
                        },
                        "id": "0037667833848532993-0000000001",
                        "paging_token": "37667833848532993-1",
                        "account": "GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE",
                        "type": "account_created",
                        "type_i": 0,
                        "created_at": "2018-05-03T13:31:45Z",
                        "starting_balance": "5.0002000"
                    },
                    {
                        "_links": {
                            "operation": {
                                "href": "https://horizon-testnet.stellar.org/operations/37667833848532995"
                            },
                            "succeeds": {
                                "href": "https://horizon-testnet.stellar.org/effects?order=desc&cursor=37667833848532995-1"
                            },
                            "precedes": {
                                "href": "https://horizon-testnet.stellar.org/effects?order=asc&cursor=37667833848532995-1"
                            }
                        },
                        "id": "0037667833848532995-0000000001",
                        "paging_token": "37667833848532995-1",
                        "account": "GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE",
                        "type": "data_created",
                        "type_i": 40,
                        "created_at": "2018-05-03T13:31:45Z"
                    }
                ]
            }
        }
        self.limit = 10

    @unittest_run_loop
    async def test_format_history_sort_asc_success(self):
        url = reverse('wallet-history', wallet_address=self.wallet_address)
        n_offset = self.history['_embedded']['records'][0]['paging_token']
        p_offset = self.history['_embedded']['records'][-1]['paging_token']
        expect = {
            '@id': url,
            'history': [{
                "id": "0037667833848532993-0000000001",
                "offset": "37667833848532993-1",
                "address": "GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE",
                "type": "account_created",
                "created_at": "2018-05-03T13:31:45Z",
                "starting_balance": "5.0002000"
            },
            {
                "id": "0037667833848532995-0000000001",
                "offset": "37667833848532995-1",
                "address": "GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE",
                "type": "data_created",
                "created_at": "2018-05-03T13:31:45Z"
            }],
            'next':  f'{url}?offset={p_offset}&limit={self.limit}&sort=asc',
            'previous': f'{url}?offset={n_offset}&limit={self.limit}&sort=desc'
        }
        actual = await format_history(history=self.history, wallet_address=self.wallet_address, limit=self.limit, sort='asc')
        assert actual == expect

    @unittest_run_loop
    async def test_format_history_sort_desc_success(self):
        url = reverse('wallet-history', wallet_address=self.wallet_address)
        n_offset = self.history['_embedded']['records'][0]['paging_token']
        p_offset = self.history['_embedded']['records'][-1]['paging_token']
        expect = {
            '@id': url,
            'history': [{
                "id": "0037667833848532993-0000000001",
                "offset": "37667833848532993-1",
                "address": "GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE",
                "type": "account_created",
                "created_at": "2018-05-03T13:31:45Z",
                "starting_balance": "5.0002000"
            },
            {
                "id": "0037667833848532995-0000000001",
                "offset": "37667833848532995-1",
                "address": "GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE",
                "type": "data_created",
                "created_at": "2018-05-03T13:31:45Z"
            }],
            'next':  f'{url}?offset={p_offset}&limit={self.limit}&sort=desc',
            'previous': f'{url}?offset={n_offset}&limit={self.limit}&sort=asc'
        }
        actual = await format_history(history=self.history, wallet_address=self.wallet_address, limit=10, sort='desc')
        assert actual == expect

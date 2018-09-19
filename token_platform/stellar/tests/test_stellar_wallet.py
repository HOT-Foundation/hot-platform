import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from tests.test_utils import BaseTestClass

from conf import settings
from stellar.wallet import get_stellar_wallet, get_transaction, get_wallet_effect

HORIZON_URL = settings['HORIZON_URL']


class TestGetWalletHistoryFromRequest(BaseTestClass):
    class SuccessResponse:
        def __init__(self):
            self.status = 200

        async def json(self):
            return {
                'account_id': 'test',
                'balances': 'test',
                'sequence': 'test',
                'data': 'test',
                'signers': 'test',
                'thresholds': 'test',
                'flags': 'test',
            }

    class NotFoundResponse:
        def __init__(self):
            self.status = 404

        async def json(self):
            return {'detail': 'test-detail'}

    class BadRequestResponse:
        def __init__(self):
            self.status = 400

        async def json(self):
            return {'detail': 'test-detail'}

    async def setUpAsync(self):
        self.wallet_address = 'test-address'
        self.transaction_hash = 'test-hash'

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_stellar_wallet_success(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.SuccessResponse()
        wallet = await get_stellar_wallet(self.wallet_address)
        url = f'{HORIZON_URL}/accounts/{self.wallet_address}'
        mock_get.assert_called_once_with(url)

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_stellar_wallet_fail(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.NotFoundResponse()
        with pytest.raises(web.HTTPNotFound) as context:
            wallet = await get_stellar_wallet(self.wallet_address)
        url = f'{HORIZON_URL}/accounts/{self.wallet_address}'
        mock_get.assert_called_once_with(url)

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_transaction_success(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.SuccessResponse()
        transaction = await get_transaction(self.transaction_hash)
        url = f'{HORIZON_URL}/transactions/{self.transaction_hash}'
        mock_get.assert_called_once_with(url)

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_transaction_fail(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.NotFoundResponse()
        with pytest.raises(web.HTTPNotFound) as context:
            transaction = await get_transaction(self.transaction_hash)
        url = f'{HORIZON_URL}/transactions/{self.transaction_hash}'
        mock_get.assert_called_once_with(url)

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_wallet_effect_success(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.SuccessResponse()
        effect = await get_wallet_effect(self.wallet_address, limit=2, offset='test-cursor')
        url = f'{HORIZON_URL}/accounts/{self.wallet_address}/effects?order=asc&limit=2&cursor=test-cursor'
        mock_get.assert_called_once_with(url)

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_wallet_effect_not_found(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.NotFoundResponse()
        with pytest.raises(web.HTTPNotFound) as context:
            effect = await get_wallet_effect(self.wallet_address)
        url = f'{HORIZON_URL}/accounts/{self.wallet_address}/effects?order=asc'
        mock_get.assert_called_once_with(url)

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_wallet_effect_bad_request(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.BadRequestResponse()
        with pytest.raises(web.HTTPBadRequest) as context:
            effect = await get_wallet_effect(self.wallet_address)
        url = f'{HORIZON_URL}/accounts/{self.wallet_address}/effects?order=asc'
        mock_get.assert_called_once_with(url)

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_wallet_effect_wrong_parameter(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.BadRequestResponse()
        with pytest.raises(ValueError) as context:
            effect = await get_wallet_effect(self.wallet_address, sort='test-sort')
        mock_get.assert_not_called()

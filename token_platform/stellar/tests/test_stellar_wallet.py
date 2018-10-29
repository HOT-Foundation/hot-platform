import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from tests.test_utils import BaseTestClass

from conf import settings
from stellar.wallet import (
    get_stellar_wallet,
    get_transaction,
    get_wallet_effect,
    get_operations_of_transaction,
    get_transaction_by_wallet,
)

HORIZON_URL = settings['HORIZON_URL']


class TestHorizonApi(BaseTestClass):
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

    class GetOperationsOfTransactionSuccess:
        def __init__(self):
            self.status = 200
            self.operation_records = [
                {
                    "_links": {
                        "self": {"href": "test-self-link"},
                        "transaction": {"href": "test-link"},
                        "effects": {"href": "test-self-link/effects"},
                        "succeeds": {"href": "success-link"},
                        "precedes": {"href": "precedes-link"},
                    },
                    "id": "test-id",
                    "paging_token": "test-paging-token",
                    "source_account": "test-source-account-address",
                    "type": "create_account",
                    "type_i": 0,
                    "created_at": "2018-10-30T06:18:30Z",
                    "transaction_hash": "test-hash",
                    "starting_balance": "10000.0000000",
                    "funder": "test-funder-address",
                    "account": "test-account-address",
                }
            ]

        async def json(self):
            return {
                "_links": {"self": {"href": "self-link"}, "next": {"href": "next-link"}, "prev": {"href": "prev-link"}},
                "_embedded": {"records": self.operation_records},
            }

    class GetTransactionBywalletSuccess:
        def __init__(self):
            self.status = 200
            self.transaction_records = [
                {
                    '_links': {
                        'self': {'href': 'test-self-link'},
                        'account': {'href': 'test-account-link'},
                        'ledger': {'href': 'test-ledger_link'},
                        'operations': {'href': 'test-operation-link}', 'templated': True},
                        'effects': {'href': 'test-effect-link', 'templated': True},
                        'precedes': {'href': 'test-precedes-link'},
                        'succeeds': {'href': 'test-succeed'},
                    },
                    'id': 'test-id',
                    'paging_token': 'test-paging_token',
                    'hash': 'test-hash',
                    'ledger': 434_802,
                    'created_at': '2018-10-30T06:18:30Z',
                    'source_account': 'test-source-account-address',
                    'source_account_sequence': '803158929876',
                    'fee_paid': 100,
                    'operation_count': 1,
                    'envelope_xdr': 'test-envelop-xdr',
                    'result_xdr': 'test-result-xdr',
                    'result_meta_xdr': 'test-result-meta-xdr',
                    'fee_meta_xdr': 'test-fee-meta-xdr',
                    'memo_type': 'none',
                    'signatures': ['test-signature'],
                }
            ]

        async def json(self):
            return {
                '_links': {'self': {'href': 'self-link'}, 'next': {'href': 'next-link'}, 'prev': {'href': 'prev-link'}},
                '_embedded': {'records': self.transaction_records},
            }

    class NotFoundResponse:
        def __init__(self):
            self.status = 404

        async def json(self):
            return {
                'type': 'https://stellar.org/horizon-errors/not_found',
                'title': 'Resource Missing',
                'status': 404,
                'detail': 'test-detail',
            }

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
        with pytest.raises(web.HTTPNotFound):
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
        with pytest.raises(web.HTTPNotFound):
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
        with pytest.raises(web.HTTPNotFound):
            effect = await get_wallet_effect(self.wallet_address)
        url = f'{HORIZON_URL}/accounts/{self.wallet_address}/effects?order=asc'
        mock_get.assert_called_once_with(url)

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_wallet_effect_bad_request(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.BadRequestResponse()
        with pytest.raises(web.HTTPBadRequest):
            effect = await get_wallet_effect(self.wallet_address)
        url = f'{HORIZON_URL}/accounts/{self.wallet_address}/effects?order=asc'
        mock_get.assert_called_once_with(url)

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_wallet_effect_wrong_parameter(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.BadRequestResponse()
        with pytest.raises(ValueError):
            effect = await get_wallet_effect(self.wallet_address, sort='test-sort')
        mock_get.assert_not_called()

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_get_transaction_by_wallet_success(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.GetTransactionBywalletSuccess()
        transactions = await get_transaction_by_wallet(self.wallet_address, limit=2, offset='test-cursor')
        url = f'{HORIZON_URL}/accounts/{self.wallet_address}/transactions?order=asc&limit=2&cursor=test-cursor'
        mock_get.assert_called_once_with(url)
        assert transactions == session.__aenter__.return_value.transaction_records

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_get_transaction_by_wallet_not_found(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.NotFoundResponse()
        with pytest.raises(web.HTTPNotFound):
            transactions = await get_transaction_by_wallet(self.wallet_address)

    @unittest_run_loop
    async def test_get_get_transaction_by_wallet_wrong_parameter(self):
        with pytest.raises(ValueError):
            transactions = await get_transaction_by_wallet(self.wallet_address, sort='test-sort')

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_operations_of_transaction_success(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.GetOperationsOfTransactionSuccess()
        transactions = await get_operations_of_transaction(self.transaction_hash, limit=2, offset='test-cursor')
        url = f'{HORIZON_URL}/transactions/{self.transaction_hash}/operations?order=asc&limit=2&cursor=test-cursor'
        mock_get.assert_called_once_with(url)
        assert transactions == session.__aenter__.return_value.operation_records

    @unittest_run_loop
    @patch('stellar.wallet.ClientSession.get')
    async def test_get_operations_of_transaction_not_found(self, mock_get):
        session = mock_get.return_value
        session.__aenter__.return_value = self.NotFoundResponse()
        with pytest.raises(web.HTTPNotFound):
            transactions = await get_operations_of_transaction(self.wallet_address)

    @unittest_run_loop
    async def test_get_operations_of_transaction_wrong_parameter(self):
        with pytest.raises(ValueError):
            transactions = await get_operations_of_transaction(self.wallet_address, sort='test-sort')

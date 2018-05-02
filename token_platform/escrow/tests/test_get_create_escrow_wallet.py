from aiohttp.test_utils import unittest_run_loop
from tests.test_utils import BaseTestClass
from asynctest import patch
from conf import settings
from escrow.get_create_escrow_wallet import (build_create_escrow_wallet_transaction,
                                             create_escrow_wallet,
                                             get_create_escrow_wallet_from_request)

class TestGetCreateEscrowWalletFromRequest(BaseTestClass):
    async def setUpAsync(self):
        self.hotnow_address = 'hotnow'
        self.escrow_address = 'escrow'
        self.merchant_address = 'merchant'
        self.expiration_date = '5/10/45'
        self.cost_per_tx = 50
        self.starting_balance = 500
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.get_create_escrow_wallet.create_escrow_wallet')
    async def test_get_create_escrow_wallet_from_request_success(self, mock):

        data = {
            'stellar_escrow_address': self.escrow_address,
            'stellar_merchant_address': self.merchant_address,
            'stellar_hotnow_address': self.hotnow_address,
            'starting_balance': 500,
            'cost_per_tx': 200
        }

        expect = {
            'escrow_address': self.escrow_address,
            '@url': '{}/create-escrow'.format(self.host),
            '@transaction_url': '{}/transaction/{}'.format(self.host, 'tx_hash'),
            'signers': [self.escrow_address, self.merchant_address, self.hotnow_address],
            'unsigned_xdr': 'unsigned_xdr'
        }

        mock.return_value = expect

        resp = await self.client.request('POST', '/create-escrow', json=data)
        assert resp.status == 200

    @unittest_run_loop
    @patch('escrow.get_create_escrow_wallet.create_escrow_wallet')
    async def test_get_create_escrow_wallet_from_request_missing_parameter(self, mock):

        expect = {
            'escrow_address': self.escrow_address,
            '@url': '{}/create-escrow'.format(self.host),
            '@transaction_url': '{}/transaction/{}'.format(self.host, 'tx_hash'),
            'signers': [self.escrow_address, self.merchant_address, self.hotnow_address],
            'unsigned_xdr': 'unsigned_xdr'
        }

        mock.return_value = expect

        data = {
            'stellar_merchant_address': self.merchant_address,
            'stellar_hotnow_address': self.hotnow_address,
            'starting_balance': 500,
            'cost_per_tx': 200
        }
        resp = await self.client.request('POST', '/create-escrow', json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter stellar_escrow_address not found. Please ensure parameters is valid.'

        data = {
            'stellar_escrow_address': self.escrow_address,
            'stellar_hotnow_address': self.hotnow_address,
            'starting_balance': 500,
            'cost_per_tx': 200
        }
        resp = await self.client.request('POST', '/create-escrow', json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter stellar_merchant_address not found. Please ensure parameters is valid.'

        data = {
            'stellar_escrow_address': self.escrow_address,
            'stellar_merchant_address': self.merchant_address,
            'starting_balance': 500,
            'cost_per_tx': 200
        }
        resp = await self.client.request('POST', '/create-escrow', json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter stellar_hotnow_address not found. Please ensure parameters is valid.'

        data = {
            'stellar_escrow_address': self.escrow_address,
            'stellar_merchant_address': self.merchant_address,
            'stellar_hotnow_address': self.hotnow_address,
            'cost_per_tx': 200
        }
        resp = await self.client.request('POST', '/create-escrow', json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter starting_balance not found. Please ensure parameters is valid.'

        data = {
            'stellar_escrow_address': self.escrow_address,
            'stellar_merchant_address': self.merchant_address,
            'stellar_hotnow_address': self.hotnow_address,
            'starting_balance': 500
        }
        resp = await self.client.request('POST', '/create-escrow', json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter cost_per_tx not found. Please ensure parameters is valid.'

    @unittest_run_loop
    @patch('escrow.get_create_escrow_wallet.create_escrow_wallet')
    async def test_get_create_escrow_wallet_from_request_wrong_value_parameter(self, mock):
        expect = {
            'escrow_address': self.escrow_address,
            '@url': '{}/create-escrow'.format(self.host),
            '@transaction_url': '{}/transaction/{}'.format(self.host, 'tx_hash'),
            'signers': [self.escrow_address, self.merchant_address, self.hotnow_address],
            'unsigned_xdr': 'unsigned_xdr'
        }

        mock.return_value = expect

        data = {
            'stellar_escrow_address': self.escrow_address,
            'stellar_merchant_address': self.merchant_address,
            'stellar_hotnow_address': self.hotnow_address,
            'starting_balance': 'make-error',
            'cost_per_tx': 200
        }

        resp = await self.client.request('POST', '/create-escrow', json=data)
        assert resp.status == 400

class TestGetCreateWallet(BaseTestClass):

    async def setUpAsync(self):
        self.tx_hash = 'tx_hash'
        self.unsigned_xdr = 'unsigned_xdr'
        self.hotnow_address = 'hotnow'
        self.escrow_address = 'escrow'
        self.merchant_address = 'merchant'
        self.cost_per_tx = 50
        self.starting_balance = 500
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.get_create_escrow_wallet.calculate_initial_xlm')
    @patch('escrow.get_create_escrow_wallet.build_create_escrow_wallet_transaction')
    async def test_get_create_escrow_wallet_success(self, mock_build, mock_cal):

        mock_build.return_value = ['unsigned_xdr', 'tx_hash']
        mock_cal.return_value = 20

        expect = {
            'escrow_address': self.escrow_address,
            '@url': '{}/create-escrow'.format(self.host),
            '@transaction_url': '{}/transaction/{}'.format(self.host, 'tx_hash'),
            'signers': [self.escrow_address, self.merchant_address, self.hotnow_address],
            'unsigned_xdr': 'unsigned_xdr'
        }

        result = await create_escrow_wallet(
            stellar_escrow_address=self.escrow_address,
            stellar_hotnow_address=self.hotnow_address,
            stellar_merchant_address=self.merchant_address,
            starting_balance=self.starting_balance,
            cost_per_tx=self.cost_per_tx
        )

        assert result == expect


class TestBuildCreateEscrowWalletTransaction(BaseTestClass):
    async def setUpAsync(self):
        self.tx_hash = 'tx_hash'
        self.unsigned_xdr = 'unsigned_xdr'
        self.hotnow_address = 'hotnow'
        self.escrow_address = 'escrow'
        self.merchant_address = 'merchant'
        self.starting_native_asset = 50
        self.starting_custom_asset = 500
        self.host = settings['HOST']

    @unittest_run_loop
    async def test_build_create_escrow_wallet_transaction(self):

        result = await build_create_escrow_wallet_transaction(
            stellar_escrow_address=self.stellar_escrow_address,
            stellar_hotnow_address=self.stellar_hotnow_address,
            stellar_merchant_address=self.stellar_merchant_address,
            starting_native_asset=self.starting_native_asset,
            starting_custom_asset=self.starting_custom_asset
        )

        expect = ['unsigned-xdr', 'tx-hash']

        assert result == expect

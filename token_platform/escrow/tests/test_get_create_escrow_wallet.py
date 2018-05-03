from decimal import Decimal

import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from stellar_base.utils import DecodeError
from tests.test_utils import BaseTestClass

from conf import settings
from escrow.get_create_escrow_wallet import (build_create_escrow_wallet_transaction,
                                             calculate_initial_xlm,
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
    async def test_get_create_escrow_wallet_from_request_with_wrong_request_data(self, mock):

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

        resp = await self.client.request('POST', '/create-escrow', data=data)
        assert resp.status == 400

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
    @patch('escrow.get_create_escrow_wallet.Builder')
    async def test_build_create_escrow_wallet_transaction_success(self, mock_builder):

        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_trust_op.return_value = 'test'
        instance.append_set_options_op.return_value = 'test'
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'

        result = await build_create_escrow_wallet_transaction(
            stellar_escrow_address=self.escrow_address,
            stellar_hotnow_address=self.hotnow_address,
            stellar_merchant_address=self.merchant_address,
            starting_native_asset=self.starting_native_asset,
            starting_custom_asset=self.starting_custom_asset
        )

        expect = ('unsigned-xdr', '74782d68617368')

        assert result == expect

    @unittest_run_loop
    @patch('escrow.get_create_escrow_wallet.Builder')
    async def test_build_create_escrow_wallet_cannot_optain_trust_op(self, mock_builder):

        def _raiseDecodeError(source, destination, code):
            raise DecodeError('Parameter is not valid.')

        def _raiseError(source, destination, code):
            raise Exception('Parameter isnot valid.')

        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_set_options_op.return_value = 'test'
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'
        instance.append_trust_op = _raiseDecodeError

        with pytest.raises(web.HTTPBadRequest):
            await build_create_escrow_wallet_transaction(
                stellar_escrow_address=self.escrow_address,
                stellar_hotnow_address=self.hotnow_address,
                stellar_merchant_address=self.merchant_address,
                starting_native_asset=self.starting_native_asset,
                starting_custom_asset=self.starting_custom_asset
            )

        instance.append_trust_op = _raiseError
        with pytest.raises(web.HTTPInternalServerError):
            await build_create_escrow_wallet_transaction(
                stellar_escrow_address=self.escrow_address,
                stellar_hotnow_address=self.hotnow_address,
                stellar_merchant_address=self.merchant_address,
                starting_native_asset=self.starting_native_asset,
                starting_custom_asset=self.starting_custom_asset
            )

    @unittest_run_loop
    @patch('escrow.get_create_escrow_wallet.Builder')
    async def test_build_create_escrow_wallet_cannot_gen_xdr(self, mock_builder):

        def _raiseError(source, destination, code):
            raise Exception('Parameter isnot valid.')

        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_trust_op.return_value = 'test'
        instance.append_set_options_op.return_value = 'test'
        instance.gen_xdr = _raiseError
        instance.te.hash_meta.return_value = b'tx-hash'

        with pytest.raises(web.HTTPBadRequest):
            await build_create_escrow_wallet_transaction(
                stellar_escrow_address=self.escrow_address,
                stellar_hotnow_address=self.hotnow_address,
                stellar_merchant_address=self.merchant_address,
                starting_native_asset=self.starting_native_asset,
                starting_custom_asset=self.starting_custom_asset
            )


class TestCalculateInitialXLM():
    async def test_calculate_initial_xlm_success(self):
        result = calculate_initial_xlm(3, 11)
        assert result == Decimal('2.5002')

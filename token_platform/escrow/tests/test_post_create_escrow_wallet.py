from decimal import Decimal

import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from stellar_base.utils import DecodeError
from tests.test_utils import BaseTestClass

from conf import settings
from escrow.post_create_escrow_wallet import (build_create_escrow_wallet_transaction,
                                             calculate_initial_xlm,
                                             create_escrow_wallet,
                                             post_create_escrow_wallet_from_request)


class TestGetCreateEscrowWalletFromRequest(BaseTestClass):
    async def setUpAsync(self):
        self.destination_address = 'hotnow'
        self.creator_address = 'creator'
        self.escrow_address = 'escrow'
        self.provider_address = 'merchant'
        self.expiration_date = '2018-05-03T09:30:06+00:00'
        self.cost_per_tx = 50
        self.starting_balance = 500
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.post_create_escrow_wallet.create_escrow_wallet')
    async def test_post_create_escrow_wallet_from_request_success(self, mock):

        data = {
            'provider_address': self.provider_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': self.starting_balance,
            'expiration_date': self.expiration_date,
            'cost_per_tx': self.cost_per_tx
        }

        expect = {
            '@id': self.escrow_address,
            'escrow_address': self.escrow_address,
            '@url': f'{self.host}/escrow/{self.escrow_address}/create-wallet',
            '@transaction_url': f'{self.host}/transaction/tx_hash',
            'signers': [self.escrow_address, self.creator_address, self.provider_address],
            'unsigned_xdr': 'unsigned_xdr'
        }

        mock.return_value = {
            'escrow_address': self.escrow_address,
            '@url': f'{self.host}/escrow/{self.escrow_address}/create-wallet',
            '@transaction_url': f'{self.host}/transaction/tx_hash',
            'signers': [self.escrow_address, self.creator_address, self.provider_address],
            'unsigned_xdr': 'unsigned_xdr'
        }

        url = f'/escrow/{self.escrow_address}/create-wallet'

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 200
        body = await resp.json()
        assert body == expect

    @unittest_run_loop
    async def test_post_create_escrow_wallet_from_request_with_plain_text_data(self):

        data = {
            'provider_address': self.provider_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 'make-error',
            'cost_per_tx': 200,
            'expiration_date': self.expiration_date,
        }

        url = f'/escrow/{self.escrow_address}/create-wallet'

        resp = await self.client.request('POST', url, data=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Request payload must be json format.'

    @unittest_run_loop
    async def test_post_create_escrow_wallet_from_request_missing_parameter(self):

        url = f'/escrow/{self.escrow_address}/create-wallet'

        data = {
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': self.starting_balance,
            'cost_per_tx': 200,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter \'provider_address\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'creator_address': self.creator_address,
            'starting_balance': self.starting_balance,
            'cost_per_tx': 200,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter \'destination_address\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'destination_address': self.destination_address,
            'starting_balance': self.starting_balance,
            'cost_per_tx': 200,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter \'creator_address\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'cost_per_tx': 200,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter \'starting_balance\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'destination_address': self.destination_address,
            'starting_balance': self.starting_balance,
            'creator_address': self.creator_address,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter \'cost_per_tx\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'destination_address': self.destination_address,
            'starting_balance': self.starting_balance,
            'creator_address': self.creator_address,
            'cost_per_tx': 200
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter \'expiration_date\' not found. Please ensure parameters is valid.'


    @unittest_run_loop
    @patch('escrow.post_create_escrow_wallet.create_escrow_wallet')
    async def test_post_create_escrow_wallet_from_request_wrong_value_parameter(self, mock):
        data = {
            'provider_address': self.provider_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 'make-error',
            'cost_per_tx': 200,
            'expiration_date': self.expiration_date,
        }

        expect = {
            'escrow_address': self.escrow_address,
            '@url': f'{self.host}/escrow/{self.escrow_address}/create-wallet',
            '@transaction_url': f'{self.host}/transaction/tx_hash',
            'signers': [self.escrow_address, self.creator_address, self.provider_address],
            'unsigned_xdr': 'unsigned_xdr'
        }

        mock.return_value = expect

        url = f'/escrow/{self.escrow_address}/create-wallet'

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter starting_balance is not valid.'

        data = {
            'provider_address': self.provider_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 2000,
            'cost_per_tx': 'make-error',
            'expiration_date': self.expiration_date,
        }

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['error'] == 'Parameter cost_per_tx is not valid.'



class TestGetCreateWallet(BaseTestClass):

    async def setUpAsync(self):
        self.tx_hash = 'tx_hash'
        self.unsigned_xdr = 'unsigned_xdr'
        self.destination_address = 'hotnow'
        self.creator_address = 'creator'
        self.escrow_address = 'escrow'
        self.provider_address = 'merchant'
        self.expiration_date = '5/10/45'
        self.cost_per_tx = 50
        self.starting_balance = 500
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.post_create_escrow_wallet.calculate_initial_xlm')
    @patch('escrow.post_create_escrow_wallet.build_create_escrow_wallet_transaction')
    async def test_create_escrow_wallet_success(self, mock_build, mock_cal):

        mock_build.return_value = ['unsigned_xdr', 'tx_hash']
        mock_cal.return_value = 20

        expect = {
            'escrow_address': self.escrow_address,
            '@url': f'{self.host}/escrow/{self.escrow_address}/create-wallet',
            '@transaction_url': f'{self.host}/transaction/tx_hash',
            'signers': [self.escrow_address, self.creator_address, self.provider_address],
            'unsigned_xdr': 'unsigned_xdr'
        }

        result = await create_escrow_wallet(
            escrow_address=self.escrow_address,
            creator_address=self.creator_address,
            provider_address=self.provider_address,
            destination_address=self.destination_address,
            starting_balance=self.starting_balance,
            expiration_date=self.expiration_date,
            cost_per_transaction=self.cost_per_tx
        )

        assert result == expect
        number_of_transaction = 500 / 50 + 2
        mock_cal.assert_called_once_with(8, number_of_transaction)


class TestBuildCreateEscrowWalletTransaction(BaseTestClass):
    async def setUpAsync(self):
        self.tx_hash = 'tx_hash'
        self.unsigned_xdr = 'unsigned_xdr'
        self.destination_address = 'hotnow'
        self.creator_address = 'creator'
        self.escrow_address = 'escrow'
        self.provider_address = 'merchant'
        self.expiration_date = '2018-05-03T09:30:06+00:00'
        self.cost_per_transaction = 20
        self.starting_native_asset = 50
        self.starting_custom_asset = 500
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.post_create_escrow_wallet.Builder')
    async def test_build_create_escrow_wallet_transaction_success(self, mock_builder):

        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_trust_op.return_value = 'test'
        instance.append_set_options_op.return_value = 'test'
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'

        result = await build_create_escrow_wallet_transaction(
            escrow_address=self.escrow_address,
            creator_address=self.creator_address,
            provider_address=self.provider_address,
            destination_address=self.destination_address,
            expiration_date = self.expiration_date,
            cost_per_transaction = self.cost_per_transaction,
            starting_native_asset=self.starting_native_asset,
            starting_custom_asset=self.starting_custom_asset
        )

        expect = ('unsigned-xdr', '74782d68617368')

        assert result == expect

    @unittest_run_loop
    @patch('escrow.post_create_escrow_wallet.Builder')
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
                escrow_address=self.escrow_address,
                creator_address=self.creator_address,
                provider_address=self.provider_address,
                destination_address=self.destination_address,
                expiration_date = self.expiration_date,
                cost_per_transaction = self.cost_per_transaction,
                starting_native_asset=self.starting_native_asset,
                starting_custom_asset=self.starting_custom_asset
            )

        instance.append_trust_op = _raiseError
        with pytest.raises(web.HTTPInternalServerError):
            await build_create_escrow_wallet_transaction(
                escrow_address=self.escrow_address,
                creator_address=self.creator_address,
                provider_address=self.provider_address,
                destination_address=self.destination_address,
                expiration_date = self.expiration_date,
                cost_per_transaction = self.cost_per_transaction,
                starting_native_asset=self.starting_native_asset,
                starting_custom_asset=self.starting_custom_asset
            )

    @unittest_run_loop
    @patch('escrow.post_create_escrow_wallet.Builder')
    async def test_build_create_escrow_wallet_cannot_gen_xdr(self, mock_builder):

        def _raiseError(source, destination, code):
            raise Exception('Parameter is not valid.')

        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_trust_op.return_value = 'test'
        instance.append_set_options_op.return_value = 'test'
        instance.gen_xdr = _raiseError
        instance.te.hash_meta.return_value = b'tx-hash'

        with pytest.raises(web.HTTPBadRequest):
            await build_create_escrow_wallet_transaction(
                escrow_address=self.escrow_address,
                creator_address=self.creator_address,
                provider_address=self.provider_address,
                destination_address=self.destination_address,
                expiration_date = self.expiration_date,
                cost_per_transaction = self.cost_per_transaction,
                starting_native_asset=self.starting_native_asset,
                starting_custom_asset=self.starting_custom_asset
            )


class TestCalculateInitialXLM():
    async def test_calculate_initial_xlm_success(self):
        result = calculate_initial_xlm(3, 11)
        assert result == Decimal('2.5002')

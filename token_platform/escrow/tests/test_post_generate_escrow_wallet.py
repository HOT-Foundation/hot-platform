
from decimal import Decimal

import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import Mock, patch
from stellar_base.utils import DecodeError
from tests.test_utils import BaseTestClass
from router import reverse

from conf import settings
from escrow.post_generate_escrow_wallet import (build_generate_escrow_wallet_transaction,
                                                calculate_initial_xlm,
                                                generate_escrow_wallet,
                                                post_generate_escrow_wallet_from_request)
from stellar.wallet import Wallet

class TestGetCreateEscrowWalletFromRequest(BaseTestClass):
    async def setUpAsync(self):
        self.destination_address = 'hotnow'
        self.creator_address = 'creator'
        self.escrow_address = 'escrow'
        self.provider_address = 'merchant'
        self.transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        self.expiration_date = '2018-05-03T09:30:06+00:00'
        self.cost_per_transaction = "50.0"
        self.starting_balance = "500.0"
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.post_generate_escrow_wallet.generate_escrow_wallet')
    async def test_post_generate_escrow_wallet_from_request_success(self, mock_wallet):

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': self.starting_balance,
            'cost_per_transaction': self.cost_per_transaction
        }

        expect = {
            '@id': reverse('escrow-generate-wallet', escrow_address=self.escrow_address),
            '@transaction_url': reverse('transaction', transaction_hash='tx_hash'),
            'signers': [self.escrow_address, self.creator_address, self.provider_address],
            'xdr': 'xdr',
            'transaction_hash': 'tx-hash'
        }

        mock_wallet.return_value = {
            '@id': reverse('escrow-generate-wallet', escrow_address=self.escrow_address),
            '@transaction_url': reverse('transaction', transaction_hash='tx_hash'),
            'signers': [self.escrow_address, self.creator_address, self.provider_address],
            'xdr': 'xdr',
            'transaction_hash': 'tx-hash'
        }

        url = reverse('escrow-generate-wallet', escrow_address=self.escrow_address)

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 200
        body = await resp.json()
        assert body == expect

    @unittest_run_loop
    @patch('escrow.post_generate_escrow_wallet.generate_escrow_wallet')
    async def test_post_generate_escrow_wallet_from_request_success_with_expiration_date(self, mock_wallet):

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': self.starting_balance,
            'cost_per_transaction': self.cost_per_transaction,
            'expiration_date': self.expiration_date
        }

        expect = {
            '@id': reverse('escrow-generate-wallet', escrow_address=self.escrow_address),
            '@transaction_url': reverse('transaction', transaction_hash='tx_hash'),
            'signers': [self.escrow_address, self.creator_address, self.provider_address],
            'xdr': 'xdr',
            'transaction_hash': 'tx-hash'
        }

        mock_wallet.return_value = {
            '@id': reverse('escrow-generate-wallet', escrow_address=self.escrow_address),
            '@transaction_url': reverse('transaction', transaction_hash='tx_hash'),
            'signers': [self.escrow_address, self.creator_address, self.provider_address],
            'xdr': 'xdr',
            'transaction_hash': 'tx-hash'
        }

        url = reverse('escrow-generate-wallet', escrow_address=self.escrow_address)

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 200
        body = await resp.json()
        assert body == expect

    @unittest_run_loop
    async def test_post_generate_escrow_wallet_from_request_with_plain_text_data(self):

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 'make-error',
            'cost_per_transaction': 200,
            'expiration_date': self.expiration_date,
        }

        url = reverse('escrow-generate-wallet', escrow_address=self.escrow_address)

        resp = await self.client.request('POST', url, data=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Request payload must be json format.'

    @unittest_run_loop
    async def test_post_generate_escrow_wallet_from_request_missing_parameter(self):

        url = reverse('escrow-generate-wallet', escrow_address=self.escrow_address)

        data = {
            'destination_address': self.destination_address,
            'transaction_source_address': self.transaction_source_address,
            'creator_address': self.creator_address,
            'starting_balance': self.starting_balance,
            'cost_per_transaction': 200,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter \'provider_address\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'creator_address': self.creator_address,
            'starting_balance': self.starting_balance,
            'cost_per_transaction': 200,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter \'destination_address\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'starting_balance': self.starting_balance,
            'cost_per_transaction': 200,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter \'creator_address\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'cost_per_transaction': 200,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter \'starting_balance\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'starting_balance': self.starting_balance,
            'creator_address': self.creator_address,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter \'cost_per_transaction\' not found. Please ensure parameters is valid.'

        data = {
            'provider_address': self.provider_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 'make-error',
            'cost_per_transaction': 200,
            'expiration_date': self.expiration_date,
        }
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter \'transaction_source_address\' not found. Please ensure parameters is valid.'

    @unittest_run_loop
    async def test_post_generate_escrow_wallet_from_request_wrong_cost_per_transaction(self):

        url = reverse('escrow-generate-wallet', escrow_address=self.escrow_address)
        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 2000,
            'cost_per_transaction': 'make-error',
            'expiration_date': self.expiration_date,
        }

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == "Can not convert to destination_address or cost_per_transaction to Decimal"

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 2000,
            'cost_per_transaction': 0,
            'expiration_date': self.expiration_date,
        }

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter cost_per_transaction is not valid.'

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 2000,
            'cost_per_transaction': -5,
            'expiration_date': self.expiration_date,
        }

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter cost_per_transaction is not valid.'


    @unittest_run_loop
    async def test_post_generate_escrow_wallet_from_request_wrong_expiration_date(self):

        url = reverse('escrow-generate-wallet', escrow_address=self.escrow_address)

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 2000,
            'cost_per_transaction': 20,
            'expiration_date': 'make-error',
        }

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == "invalid literal for int() with base 10: b'make'"

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 2000,
            'cost_per_transaction': 20,
            'expiration_date': '2018-05-08T01:38:25',
        }

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter expiration date is not valid.'


    @unittest_run_loop
    async def test_post_generate_escrow_wallet_from_request_wrong_starting_balance(self):
        url = reverse('escrow-generate-wallet', escrow_address=self.escrow_address)

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 'make-error',
            'cost_per_transaction': 200,
            'expiration_date': self.expiration_date,
        }

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == "Can not convert to destination_address or cost_per_transaction to Decimal"

        data = {
            'provider_address': self.provider_address,
            'transaction_source_address': self.transaction_source_address,
            'destination_address': self.destination_address,
            'creator_address': self.creator_address,
            'starting_balance': 2000,
            'cost_per_transaction': 3,
            'expiration_date': self.expiration_date,
        }

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        body = await resp.json()
        assert body['message'] == 'Parameter starting_balance is not match with cost_per_transaction.'


class TestGetCreateWallet(BaseTestClass):

    async def setUpAsync(self):
        self.tx_hash = 'tx_hash'
        self.xdr = 'xdr'
        self.destination_address = 'hotnow'
        self.transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        self.creator_address = 'creator'
        self.escrow_address = 'escrow'
        self.provider_address = 'merchant'
        self.expiration_date = '5/10/45'
        self.cost_per_transaction = 50
        self.starting_balance = 500
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.post_generate_escrow_wallet.get_stellar_wallet')
    @patch('escrow.post_generate_escrow_wallet.calculate_initial_xlm')
    @patch('escrow.post_generate_escrow_wallet.build_generate_escrow_wallet_transaction')
    async def test_generate_escrow_wallet_success(self, mock_build, mock_cal, mock_get_stellar_wallet):

        mock_build.return_value = ['xdr', 'tx_hash']
        mock_cal.return_value = 20
        mock_get_stellar_wallet.return_value = Wallet(
            "1",
            [],
            "1",
            {},
            [],
            {},
            {}
        )
        expect = {
            '@id': reverse('escrow-generate-wallet', escrow_address=self.escrow_address),
            '@transaction_url': reverse('transaction', transaction_hash='tx_hash'),
            'signers': [self.escrow_address, self.creator_address, self.provider_address],
            'xdr': 'xdr',
            'transaction_hash': 'tx_hash'
        }

        result = await generate_escrow_wallet(
            escrow_address=self.escrow_address,
            transaction_source_address=self.transaction_source_address,
            creator_address=self.creator_address,
            provider_address=self.provider_address,
            destination_address=self.destination_address,
            starting_balance=self.starting_balance,
            expiration_date=self.expiration_date,
            cost_per_transaction=self.cost_per_transaction
        )

        assert result == expect
        number_of_transaction = 500 / 50 + 2
        mock_cal.assert_called_once_with(8, number_of_transaction)


class TestBuildCreateEscrowWalletTransaction(BaseTestClass):
    async def setUpAsync(self):
        self.tx_hash = 'tx_hash'
        self.xdr = 'xdr'
        self.destination_address = 'hotnow'
        self.creator_address = 'creator'
        self.transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        self.escrow_address = 'escrow'
        self.provider_address = 'merchant'
        self.expiration_date = '2018-05-03T09:30:06+00:00'
        self.cost_per_transaction = 20
        self.starting_native_asset = 50
        self.starting_custom_asset = 500
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.post_generate_escrow_wallet.Builder')
    async def test_build_generate_escrow_wallet_transaction_success(self, mock_builder):

        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_trust_op.return_value = 'test'
        instance.append_set_options_op.return_value = 'test'
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'

        result = await build_generate_escrow_wallet_transaction(
            escrow_address=self.escrow_address,
            transaction_source_address=self.transaction_source_address,
            creator_address=self.creator_address,
            provider_address=self.provider_address,
            destination_address=self.destination_address,
            expiration_date=self.expiration_date,
            cost_per_transaction=self.cost_per_transaction,
            starting_native_asset=self.starting_native_asset,
            starting_custom_asset=self.starting_custom_asset
        )

        expect = ('unsigned-xdr', '74782d68617368')

        assert result == expect

    @unittest_run_loop
    @patch('escrow.post_generate_escrow_wallet.Builder')
    async def test_build_generate_escrow_wallet_cannot_optain_trust_op(self, mock_builder):

        def _raiseDecodeError(source, destination, code, limit):
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
            await build_generate_escrow_wallet_transaction(
                escrow_address=self.escrow_address,
                transaction_source_address=self.transaction_source_address,
                creator_address=self.creator_address,
                provider_address=self.provider_address,
                destination_address=self.destination_address,
                expiration_date=self.expiration_date,
                cost_per_transaction=self.cost_per_transaction,
                starting_native_asset=self.starting_native_asset,
                starting_custom_asset=self.starting_custom_asset
            )

        instance.append_trust_op = _raiseError
        with pytest.raises(web.HTTPInternalServerError):
            await build_generate_escrow_wallet_transaction(
                escrow_address=self.escrow_address,
                transaction_source_address=self.transaction_source_address,
                creator_address=self.creator_address,
                provider_address=self.provider_address,
                destination_address=self.destination_address,
                expiration_date=self.expiration_date,
                cost_per_transaction=self.cost_per_transaction,
                starting_native_asset=self.starting_native_asset,
                starting_custom_asset=self.starting_custom_asset
            )

    @unittest_run_loop
    @patch('escrow.post_generate_escrow_wallet.Builder')
    async def test_build_generate_escrow_wallet_cannot_gen_xdr(self, mock_builder):

        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_trust_op.return_value = 'test'
        instance.append_set_options_op.return_value = 'test'
        instance.gen_xdr = Exception('Parameter is not valid.')
        instance.te.hash_meta.return_value = b'tx-hash'

        with pytest.raises(web.HTTPBadRequest):
            await build_generate_escrow_wallet_transaction(
                escrow_address=self.escrow_address,
                transaction_source_address=self.transaction_source_address,
                creator_address=self.creator_address,
                provider_address=self.provider_address,
                destination_address=self.destination_address,
                expiration_date=self.expiration_date,
                cost_per_transaction=self.cost_per_transaction,
                starting_native_asset=self.starting_native_asset,
                starting_custom_asset=self.starting_custom_asset
            )


class TestCalculateInitialXLM():
    async def test_calculate_initial_xlm_success(self):
        result = calculate_initial_xlm(3, 11)
        assert result == Decimal('2.6')

    async def test_calculate_initial_xlm_wrong_parameter(self):
        with pytest.raises(ValueError):
            calculate_initial_xlm(-1, -11)

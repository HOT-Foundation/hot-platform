import pytest

from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from tests.test_utils import BaseTestClass
from asynctest import patch
from router import reverse
from conf import settings
from decimal import Decimal
from escrow.post_close_escrow_wallet import (generate_close_escrow_wallet, build_generate_close_escrow_wallet_transaction)

class TestPostCloseEscrowWalletFromRequest(BaseTestClass):
    async def setUpAsync(self):
        self.escrow_address = 'escrow'
        self.provider_address = 'provider'
        self.creator_address = 'creator'
        self.tx_hash = 'tx_tash'
        self.unsigned_xdr = 'xdr'
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.post_close_escrow_wallet.generate_close_escrow_wallet')
    async def test_post_close_escrow_wallet_from_request_success(self, mock_generate_claose_escrow_wallet):

        mock_generate_claose_escrow_wallet.return_value = {
            'escrow_address' : self.escrow_address,
            'transaction_url' : reverse('transaction', transaction_hash=self.tx_hash),
            'signers' : [self.provider_address, self.creator_address],
            'xdr' : self.unsigned_xdr,
            'transaction_hash' : self.tx_hash
        }

        expect = {
            '@id' : reverse('close-escrow-wallet', escrow_address=self.escrow_address),
            'escrow_address' : self.escrow_address,
            'transaction_url' : reverse('transaction', transaction_hash=self.tx_hash),
            'signers' : [self.provider_address, self.creator_address],
            'xdr' : self.unsigned_xdr,
            'transaction_hash' : self.tx_hash
        }

        url = f"{self.host}{reverse('close-escrow-wallet', escrow_address=self.escrow_address)}"
        resp = await self.client.request('POST', url)
        assert resp.status == 200
        text = await resp.json()
        assert text == expect

class TestGenerateCloseEscrowWallet(BaseTestClass):
    async def setUpAsync(self):
        self.escrow_address = 'escrow'
        self.provider_address = 'provider'
        self.creator_address = 'creator'
        self.tx_hash = 'tx_tash'
        self.unsigned_xdr = 'xdr'
        self.remain_custom_asset = '100'
        self.custom_asset = settings['ASSET_CODE']

    @unittest_run_loop
    @patch('escrow.post_close_escrow_wallet.get_escrow_wallet_detail')
    @patch('escrow.post_close_escrow_wallet.build_generate_close_escrow_wallet_transaction')
    async def test_generate_close_escrow_wallet_success(self, mock_build_transaction, mock_escrow_wallet_detail):

        mock_escrow_wallet_detail.return_value = {
            '@id': self.escrow_address,
            '@url': reverse('escrow-address', escrow_address=self.escrow_address),
            'asset': {
                self.custom_asset : self.remain_custom_asset
            },
            'generate-wallet': reverse('escrow-generate-wallet', escrow_address=self.escrow_address),
            'data': {
                'provider_address' : self.provider_address,
                'creator_address' : self.creator_address
            },
            'signers' : [self.provider_address, self.creator_address]
        }

        mock_build_transaction.return_value = (self.unsigned_xdr, self.tx_hash)

        expect = {
            'escrow_address' : self.escrow_address,
            'transaction_url' : reverse('transaction', transaction_hash=self.tx_hash),
            'signers' : [self.provider_address, self.creator_address],
            'xdr' : self.unsigned_xdr,
            'transaction_hash' : self.tx_hash
        }

        result = await generate_close_escrow_wallet(escrow_address=self.escrow_address)

        assert result == expect

class TestBuildGenerateCloseEscrowWalletTransaction(BaseTestClass):
    async def setUpAsync(self):
        self.escrow_address = 'escrow'
        self.provider_address = 'provider'
        self.creator_address = 'creator'
        self.remain_custom_asset = '100'
        self.custom_asset = settings['ASSET_CODE']
        self.escrow_wallet_detail = {
            '@id': self.escrow_address,
            '@url': reverse('escrow-address', escrow_address=self.escrow_address),
            'asset': {
                self.custom_asset : self.remain_custom_asset
            },
            'generate-wallet': reverse('escrow-generate-wallet', escrow_address=self.escrow_address),
            'data': {
                'provider_address' : self.provider_address,
                'creator_address' : self.creator_address
            },
            'signers' : [self.provider_address, self.creator_address]
        }


    @unittest_run_loop
    @patch('escrow.post_close_escrow_wallet.Builder')
    async def test_build_generate_close_escrow_wallet_transaction_success(self, mock_builder):
        self.escrow_wallet_detail['asset'][self.custom_asset] = '100.00000'
        remain_custom_asset = Decimal(self.escrow_wallet_detail['asset'][self.custom_asset])
        instance = mock_builder.return_value
        instance.append_payment_op.return_value = 'payment_op'
        instance.append_account_merge_op.return_value = 'account_merge'
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'

        result = await build_generate_close_escrow_wallet_transaction(self.escrow_wallet_detail)

        expect = ('unsigned-xdr', '74782d68617368')
        assert result == expect
        instance.append_payment_op.assert_called_once_with(destination=self.provider_address, amount=remain_custom_asset, asset_type=self.custom_asset, asset_issuer=settings['ISSUER'], source=self.escrow_address)

    @unittest_run_loop
    @patch('escrow.post_close_escrow_wallet.Builder')
    async def test_build_generate_close_escrow_wallet_transaction_not_have_remain_amount(self, mock_builder):
        self.escrow_wallet_detail['asset'][self.custom_asset] = '0'

        instance = mock_builder.return_value
        instance.append_account_merge_op.return_value = 'account_merge'
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'

        result = await build_generate_close_escrow_wallet_transaction(self.escrow_wallet_detail)

        expect = ('unsigned-xdr', '74782d68617368')
        assert result == expect

    @unittest_run_loop
    @patch('escrow.post_close_escrow_wallet.Builder')
    async def test_build_generate_close_escrow_wallet_transaction_cannot_gen_xdr(self, mock_builder):

        self.escrow_wallet_detail['asset'][self.custom_asset] = '100.0000'

        instance = mock_builder.return_value
        instance.append_payment_op.return_value = 'payment_op'
        instance.append_account_merge_op.return_value = 'account_merge'
        instance.gen_xdr = Exception('Parameter is not valid.')
        instance.te.hash_meta.return_value = b'tx-hash'

        with pytest.raises(web.HTTPBadRequest):
            await build_generate_close_escrow_wallet_transaction(self.escrow_wallet_detail)



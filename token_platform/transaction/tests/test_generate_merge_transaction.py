import pytest

from tests.test_utils import BaseTestClass
from aiohttp.test_utils import unittest_run_loop
from aiohttp import web
from asynctest import patch
from conf import settings
from router import reverse
from decimal import Decimal
from typing import List
from stellar_base.builder import Builder
from stellar_base.stellarxdr import StellarXDR_const as const
from transaction.generate_merge_transaction import (generate_merge_transaction, build_payment_operation, build_remove_trustlines_operation, build_remove_manage_data_operation, build_account_merge_operation, build_generate_merge_transaction, generate_parties_wallet, is_match_balance, get_creator_address)


class TestGenerateMergeTransaction(BaseTestClass):
    async def setUpAsync(self):
        self.wallet_address = 'wallet_address'
        self.custom_asset = settings['ASSET_CODE']
        self.remain_custom_asset = '100.0000'
        self.provider_address = 'provider_address'
        self.creator_address = 'creator_address'
        self.tx_hash = 'tx_tash'
        self.unsigned_xdr = 'xdr'
        self.parties_wallet = [
            {'address' : 'wallet1', 'amount' : '15'},
            {'address' : 'wallet2', 'amount' : '20'}
        ]
        self.wallet_detail = {
            '@id': self.wallet_address,
            '@url': reverse('escrow-address', escrow_address=self.wallet_address),
            'asset': {
                self.custom_asset : self.remain_custom_asset
            },
            'generate-wallet': reverse('escrow-generate-wallet', escrow_address=self.wallet_address),
            'data': {
                'provider_address' : self.provider_address,
                'creator_address' : self.creator_address
            },
            'signers' : [self.provider_address, self.creator_address]
        }

    @unittest_run_loop
    @patch('transaction.generate_merge_transaction.build_generate_merge_transaction')
    @patch('transaction.generate_merge_transaction.get_escrow_wallet_detail')
    async def test_generate_merge_transaction_success(self, mock_wallet_detail, mock_merge_transaction):
        mock_wallet_detail.return_value = self.wallet_detail
        mock_merge_transaction.return_value = self.unsigned_xdr, self.tx_hash

        result = await generate_merge_transaction(self.wallet_address, self.parties_wallet)

        expect = {
            'wallet_address' : self.wallet_address,
            'transaction_url' : reverse('transaction', transaction_hash=self.tx_hash),
            'signers' : self.wallet_detail['signers'],
            'xdr' : self.unsigned_xdr,
            'transaction_hash' : self.tx_hash
        }

        assert result == expect


class TestBuildGenerateMergeTransaction(BaseTestClass):
    async def setUpAsync(self):
        self.wallet_address = 'wallet_address'
        self.provider_address = 'provider_address'
        self.creator_address = 'creator_address'
        self.parties_wallet = [
            {'address' : 'wallet1', 'amount' : '15'},
            {'address' : 'wallet2', 'amount' : '20'}
        ]
        self.wallet_detail = {
            '@id': self.wallet_address,
            '@url': reverse('escrow-address', escrow_address=self.wallet_address),
            'asset': {
                settings['ASSET_CODE'] : '100.0000'
            },
            'generate-wallet': reverse('escrow-generate-wallet', escrow_address=self.wallet_address),
            'data': {
                'provider_address' : self.provider_address,
                'creator_address' : self.creator_address
            },
            'signers' : [self.provider_address, self.creator_address]
        }

    @unittest_run_loop
    @patch('transaction.generate_merge_transaction.is_match_balance')
    @patch('transaction.generate_merge_transaction.Builder')
    async def test_build_generate_merge_transaction_success(self, mock_builder, mock_is_match):
        instance = mock_builder.return_value
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'
        mock_is_match.return_value = True

        result = await build_generate_merge_transaction(self.wallet_detail, self.parties_wallet)
        expect = ('unsigned-xdr', '74782d68617368')
        assert result == expect

    @unittest_run_loop
    @patch('transaction.generate_merge_transaction.get_creator_address')
    @patch('transaction.generate_merge_transaction.is_match_balance')
    @patch('transaction.generate_merge_transaction.Builder')
    async def test_build_generate_merge_transaction_creator_is_none(self, mock_builder, mock_is_match, mock_get_creator):
        instance = mock_builder.return_value
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'
        mock_is_match.return_value = True
        mock_get_creator.return_value = self.creator_address
        self.wallet_detail['data'] = {}

        result = await build_generate_merge_transaction(self.wallet_detail, self.parties_wallet)
        expect = ('unsigned-xdr', '74782d68617368')
        assert result == expect

    @unittest_run_loop
    @patch('transaction.generate_merge_transaction.is_match_balance')
    @patch('transaction.generate_merge_transaction.Builder')
    async def test_build_generate_merge_transaction_none_parties(self, mock_builder, mock_is_match):
        instance = mock_builder.return_value
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'
        mock_is_match.return_value = True

        result = await build_generate_merge_transaction(self.wallet_detail)
        expect = ('unsigned-xdr', '74782d68617368')
        assert result == expect

    @unittest_run_loop
    @patch('transaction.generate_merge_transaction.is_match_balance')
    @patch('transaction.generate_merge_transaction.Builder')
    async def test_build_generate_merge_transaction_cannot_gen_xdr(self, mock_builder, mock_is_match):
        instance = mock_builder.return_value
        instance.gen_xdr = Exception('Parameter is not valid.')
        instance.te.hash_meta.return_value = b'tx-hash'
        mock_is_match.return_value = True

        with pytest.raises(web.HTTPBadRequest):
            await build_generate_merge_transaction(self.wallet_detail, self.parties_wallet)

    @unittest_run_loop
    @patch('transaction.generate_merge_transaction.is_match_balance')
    async def test_build_generate_merge_transaction_balance_not_match(self, mock_is_match):

        mock_is_match.return_value = False

        with pytest.raises(web.HTTPBadRequest):
            await build_generate_merge_transaction(self.wallet_detail, self.parties_wallet)


class TestGetCreatorAddress(BaseTestClass):
    async def setUpAsync(self):
        self.wallet_address = 'wallet_address'
        self.result = { "_embedded": {"records": [
                            {'source_account' : 'source_account'}
                      ]}}

    @unittest_run_loop
    @patch('transaction.generate_merge_transaction.horizon_livenet')
    @patch('transaction.generate_merge_transaction.horizon_testnet')
    async def test_get_creator_address_success(self, mock_testnet, mock_livenet):
        instance = mock_testnet.return_value
        instance.account_operations.return_value = self.result

        instance = mock_livenet.return_value
        instance.account_operations.return_value = self.result

        result = await get_creator_address(self.wallet_address)

        assert result == 'source_account'


class TestGeneratePartiesWallet(BaseTestClass):
    async def setUpAsync(self):
        self.wallet_address = 'wallet_address'
        self.provider_address = 'provider_address'
        self.creator_address = 'creator_address'
        self.wallet_detail = {
            '@id': self.wallet_address,
            '@url': reverse('escrow-address', escrow_address=self.wallet_address),
            'asset': {
                settings['ASSET_CODE'] : '100.0000'
            },
            'generate-wallet': reverse('escrow-generate-wallet', escrow_address=self.wallet_address),
            'data': {
                'provider_address' : self.provider_address,
                'creator_address' : self.creator_address
            },
            'signers' : [self.provider_address, self.creator_address]
        }

    @unittest_run_loop
    async def test_generate_parties_wallet_success(self):
        result = await generate_parties_wallet(self.wallet_detail)
        expect = [
            {'address' : self.provider_address, 'amount' : self.wallet_detail['asset'][settings['ASSET_CODE']]}
        ]

        assert isinstance(result, List)
        assert result == expect


class TestIsMatchBalance(BaseTestClass):
    async def setUpAsync(self):
        self.parties_wallet = [
            {'address' : 'wallet1', 'amount' : '15'},
            {'address' : 'wallet2', 'amount' : '20'}
        ]

    @unittest_run_loop
    async def test_is_match_balance_success(self):
        balance = Decimal('35')
        result = await is_match_balance(self.parties_wallet, balance)

        assert result is True

    @unittest_run_loop
    async def test_is_match_balance_fail(self):
        balance = Decimal('40')
        result = await is_match_balance(self.parties_wallet, balance)

        assert result is False


class TestBuildPaymentOperation(BaseTestClass):
    async def setUpAsync(self):
        self.builder = Builder(address='GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE')
        self.source_address = 'GCEOD3ALYS3I7PVF5PZ3JJDNQF2AWKX5IOWWPC4RBHQVJFR6LXEFOMZ3'
        self.destination_address = 'GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE'


    @unittest_run_loop
    async def test_build_payment_operation_success(self):
        parties_wallet = [
            {'address' : 'GCEOD3ALYS3I7PVF5PZ3JJDNQF2AWKX5IOWWPC4RBHQVJFR6LXEFOMZ3', 'amount' : '15'},
            {'address' : 'GD3PPDLKXRDM57UV7QDFIHLLRCLM4KGVIA43GEM7ZOT7EHK5TR3Z5G6I', 'amount' : '20'}
        ]

        await build_payment_operation(self.builder, self.source_address, parties_wallet)
        operation = self.builder.ops[-1].to_xdr_object()

        assert len(self.builder.ops) == len(parties_wallet)
        assert operation.type == const.PAYMENT


    @unittest_run_loop
    async def test_build_payment_operation_fail(self):

        parties_wallet = [
            {'address' : 'GCEOD3ALYS3I7PVF5PZ3JJDNQF2AWKX5IOWWPC4RBHQVJFR6LXEFOMZ3', 'amount' : '0'},
            {'address' : 'GD3PPDLKXRDM57UV7QDFIHLLRCLM4KGVIA43GEM7ZOT7EHK5TR3Z5G6I', 'amount' : '0'}
        ]
        await build_payment_operation(self.builder, self.source_address, parties_wallet)

        assert len(self.builder.ops) == 0
        assert self.builder.ops == []


class TestBuildRemoveTrustlinesOperation(BaseTestClass):
    async def setUpAsync(self):
        self.builder = Builder(address='GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE')
        self.source_address = 'GCEOD3ALYS3I7PVF5PZ3JJDNQF2AWKX5IOWWPC4RBHQVJFR6LXEFOMZ3'

    @unittest_run_loop
    async def test_build_remove_trustlins_operation_success(self):
        await build_remove_trustlines_operation(self.builder, self.source_address)
        operation = self.builder.ops[-1].to_xdr_object()

        assert operation.type == const.CHANGE_TRUST


class TestBuildRemoveManageDataOperation(BaseTestClass):
    async def setUpAsync(self):
        self.builder = Builder(address='GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE')
        self.source_address = 'GCEOD3ALYS3I7PVF5PZ3JJDNQF2AWKX5IOWWPC4RBHQVJFR6LXEFOMZ3'
        self.key_list = ['key1', 'key2', 'key3']

    @unittest_run_loop
    async def test_build_remove_manage_data_operation_success(self):
        await build_remove_manage_data_operation(self.builder, self.source_address, self.key_list)
        operation = self.builder.ops[-1].to_xdr_object()

        assert len(self.builder.ops) == len(self.key_list)
        assert operation.type == const.MANAGE_DATA


class TestBuildAccountMergeOperation(BaseTestClass):
    async def setUpAsync(self):
        self.builder = Builder(address='GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE')
        self.source_address = 'GCEOD3ALYS3I7PVF5PZ3JJDNQF2AWKX5IOWWPC4RBHQVJFR6LXEFOMZ3'
        self.destination_address = 'GDHZCRVQP3W3GUSZMC3ECHRG3WVQQZXVDHY5TOQ5AB5JKRSSUUZ6XDUE'

    @unittest_run_loop
    async def test_build_account_merge_operation_success(self):
        await build_account_merge_operation(self.builder, self.source_address, self.destination_address)
        operation = self.builder.ops[-1].to_xdr_object()

        assert operation.type == const.ACCOUNT_MERGE

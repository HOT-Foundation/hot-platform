import binascii

import pytest
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from stellar_base.keypair import Keypair
from stellar_base.utils import AccountNotExistError, StellarMnemonic
from tests.test_utils import BaseTestClass

from conf import settings
from wallet.wallet import (build_create_wallet_transaction,
                           wallet_address_is_duplicate)


class MockBuilder():

    def __init__(self):
        self.te = 'hash'


class TestCreateWallet(BaseTestClass):
    """Test cases for building unsigned transaction for creating wallet."""
    async def setUpAsync(self):
        sm = StellarMnemonic("english")
        secret_phrase = sm.generate()
        kp = Keypair.deterministic(secret_phrase, lang='english')
        self.wallet_address = 'GB6PGEFJSXPRUNYAJXH4OZNIZNCEXC6B2JMV5RUGWJECWVWNCJTMGJB4'
        self.target_address = kp.address().decode()
        self.starting_amount = 600
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('wallet.get_create_wallet.Builder')
    @patch('wallet.get_create_wallet.wallet_address_is_duplicate')
    @patch('wallet.get_create_wallet.build_create_wallet_transaction')
    async def test_get_create_wallet_from_request_success(self, mock_xdr, mock_check, mock_te):
        mock_te.return_value = MockBuilder()
        mock_xdr.return_value = (b'test-xdr', b'test-transaction-envelop')
        mock_check.return_value = False
        url = f'/wallet/{self.wallet_address}/create-wallet?target-address={self.target_address}&starting-amount={self.starting_amount}'
        resp = await self.client.request("GET", url)
        assert resp.status == 200
        text = await resp.json()
        hash = MockBuilder()
        expect_tx_hash = binascii.hexlify(mock_xdr.return_value[1]).decode()
        expect_unsigned_xdr = mock_xdr.return_value[0].decode()
        expect = {
            'source_address': self.wallet_address,
            'signers': [self.wallet_address, self.target_address],
            'unsigned_xdr': expect_unsigned_xdr,
            'transaction_url': f'{self.host}/transaction/{expect_tx_hash}',
            '@url': f'{self.host}{url}'
        }
        assert text == expect

    @unittest_run_loop
    async def test_get_create_wallet_from_request_use_wrong_parameter(self):
        url = f'/wallet/{self.wallet_address}/create-wallet?target=test'
        resp = await self.client.request("GET", url)
        assert resp.status == 400
        text = await resp.json()
        assert 'Bad request, parameter missing.' in text['error']

        url = f'/wallet/{self.wallet_address}/create-wallet?target=test&value=0'
        resp = await self.client.request("GET", url)
        assert resp.status == 400
        text = await resp.json()
        assert 'Bad request, parameter missing.' in text['error']

        url = f'/wallet/{self.wallet_address}/create-wallet?value=500'
        resp = await self.client.request("GET", url)
        assert resp.status == 400
        text = await resp.json()
        assert 'Bad request, parameter missing.' in text['error']

    @patch('wallet.wallet.StellarAddress.get', **{'side_effect': ValueError})
    def test_wallet_address_is_duplicate_with_value_error(self, mock):
        result = wallet_address_is_duplicate(self.target_address)
        assert result == True

    @patch('wallet.wallet.StellarAddress.get', **{'side_effect': AccountNotExistError('test error')})
    def test_wallet_address_is_duplicate_with_account_not_existing_errir(self, mock):
        result = wallet_address_is_duplicate(self.target_address)
        assert result == False

    @patch('wallet.wallet.StellarAddress.get', **{'return_value': True})
    def test_wallet_address_is_duplicate_fail(self, mock):
        result = wallet_address_is_duplicate(self.wallet_address)
        assert result == True

import binascii

import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from stellar_base.exceptions import AccountNotExistError, HorizonError
from stellar_base.keypair import Keypair
from stellar_base.utils import StellarMnemonic
from tests.test_utils import BaseTestClass

from conf import settings
from router import reverse
from stellar.wallet import Wallet
from wallet.wallet import (build_generate_trust_wallet_transaction,
                           wallet_address_is_duplicate)


class TestCreateTrustWallet(BaseTestClass):
    """Test cases for building unsigned transaction for creating wallet."""
    async def setUpAsync(self):
        sm = StellarMnemonic("english")
        secret_phrase = sm.generate()
        kp = Keypair.deterministic(secret_phrase, lang='english')
        self.wallet_address = 'GB6PGEFJSXPRUNYAJXH4OZNIZNCEXC6B2JMV5RUGWJECWVWNCJTMGJB4'
        self.transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        self.target_address = kp.address().decode()
        self.xlm_amount = 600
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('wallet.post_generate_trust_wallet.wallet_address_is_duplicate')
    @patch('wallet.post_generate_trust_wallet.get_wallet')
    @patch('wallet.post_generate_trust_wallet.build_generate_trust_wallet_transaction')
    async def test_post_generate_trust_wallet_from_request_success(self, mock_xdr, get_wallet, mock_check):
        mock_xdr.return_value = (b'test-xdr', b'test-transaction-envelop')
        get_wallet.return_value = Wallet(
                "1",
                [],
                "1",
                {},
                [],
                {},
                {}
            )
        mock_check.return_value = False

        url = reverse('generate-trust-wallet', wallet_address=self.wallet_address)
        json_request = {
            'target_address' : self.target_address,
            'transaction_source_address': self.transaction_source_address,
            'xlm_amount' : self.xlm_amount
        }

        resp = await self.client.request("POST", url, json=json_request)
        assert resp.status == 200
        text = await resp.json()
        expect_tx_hash = binascii.hexlify(mock_xdr.return_value[1]).decode()
        expect_unsigned_xdr = mock_xdr.return_value[0].decode()
        expect = {
            'source_address': self.wallet_address,
            'transaction_source_address': self.transaction_source_address,
            'signers': [self.wallet_address, self.target_address, self.transaction_source_address],
            'xdr': expect_unsigned_xdr,
            'transaction_url': f"{self.host}{reverse('transaction', transaction_hash=expect_tx_hash)}",
            'transaction_hash': expect_tx_hash,
            '@id': f'{self.host}{url}'
        }
        assert text == expect

    @unittest_run_loop
    async def test_post_generate_trust_wallet_from_request_json_data_missing(self):
        url = reverse('generate-trust-wallet', wallet_address=self.wallet_address)
        resp = await self.client.request("POST", url)
        assert resp.status == 400
        text = await resp.json()
        assert 'Bad request, JSON data missing.' in text['message']

    @unittest_run_loop
    async def test_post_generate_trust_wallet_from_request_missing_param(self):
        url = reverse('generate-trust-wallet', wallet_address=self.wallet_address)
        resp = await self.client.request("POST", url, json={'target_address':'test', 'xlm_amount':'10'})
        assert resp.status == 400
        text = await resp.json()
        assert text['message'] == 'Parameter \'transaction_source_address\' not found. Please ensure parameters is valid.'

    @unittest_run_loop
    async def test_post_generate_trust_wallet_from_request_use_wrong_parameter(self):
        url = reverse('generate-trust-wallet', wallet_address=self.wallet_address)
        resp = await self.client.request("POST", url, json={'target':'test', 'transaction_source_address': 'test'})
        assert resp.status == 400
        text = await resp.json()
        assert "Parameter 'target_address' not found. Please ensure parameters is valid." in text['message']

        resp = await self.client.request("POST", url, json={
                                         'target_address' : 'test', 'transaction_source_address': 'test'})
        assert resp.status == 400
        text = await resp.json()
        assert 'XLM balance must have more than 0.' in text['message']

        resp = await self.client.request("POST", url, json={
                                         'target_address' : 'test',
                                         'transaction_source_address': 'test',
                                         'xlm_amount' : 'not_Decimal'})
        assert resp.status == 400
        text = await resp.json()
        assert "not_Decimal is not decimal" in text['message']

        resp = await self.client.request("POST", url, json={
                                         'target_address' : 'test',
                                         'transaction_source_address': 'test',
                                         'xlm_amount' : '5',
                                         'htkn_amount' : 'not_Decimal'})
        assert resp.status == 400
        text = await resp.json()
        assert "not_Decimal is not decimal" in text['message']


    @unittest_run_loop
    @patch('wallet.post_generate_trust_wallet.wallet_address_is_duplicate', **{'return_value' : True})
    async def test_post_generate_trust_wallet_from_request_is_duplicate_wallet_address(self, mock):
        url = reverse('generate-trust-wallet', wallet_address=self.wallet_address)
        json_request = {
            'target_address' : self.target_address,
            'transaction_source_address': self.transaction_source_address,
            'xlm_amount' : self.xlm_amount
        }

        result = await self.client.request("POST", url, json=json_request)
        assert result.status == 400
        text = await result.json()
        assert 'Target address is already used.' in text['message']

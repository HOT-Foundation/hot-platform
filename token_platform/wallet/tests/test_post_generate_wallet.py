import binascii

import pytest
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from stellar_base.keypair import Keypair
from stellar_base.utils import StellarMnemonic
from stellar_base.exceptions import AccountNotExistError
from tests.test_utils import BaseTestClass
from aiohttp import web

from conf import settings
from wallet.wallet import (build_generate_wallet_transaction,
                           wallet_address_is_duplicate)
from router import reverse


class TestCreateWallet(BaseTestClass):
    """Test cases for building unsigned transaction for creating wallet."""
    async def setUpAsync(self):
        sm = StellarMnemonic("english")
        secret_phrase = sm.generate()
        kp = Keypair.deterministic(secret_phrase, lang='english')
        self.wallet_address = 'GB6PGEFJSXPRUNYAJXH4OZNIZNCEXC6B2JMV5RUGWJECWVWNCJTMGJB4'
        self.transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        self.target_address = kp.address().decode()
        self.amount_xlm = 600
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('wallet.post_generate_wallet.get_signers')
    @patch('wallet.post_generate_wallet.wallet_address_is_duplicate')
    @patch('wallet.post_generate_wallet.build_generate_wallet_transaction')
    async def test_post_generate_wallet_from_request_success(self, mock_xdr, mock_check, mock_signers):
        mock_signers.return_value = [{
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "weight": 1
        }]
        mock_xdr.return_value = (b'test-xdr', b'test-transaction-envelop')
        mock_check.return_value = False

        url = reverse('generate-wallet', wallet_address=self.wallet_address)
        json_request = {
            'target_address' : self.target_address,
            'transaction_source_address': self.transaction_source_address,
            'amount_xlm' : self.amount_xlm
        }

        resp = await self.client.request("POST", url, json=json_request)
        assert resp.status == 200
        text = await resp.json()
        expect_tx_hash = binascii.hexlify(mock_xdr.return_value[1]).decode()
        expect_unsigned_xdr = mock_xdr.return_value[0].decode()
        expect = {
            'source_address': self.wallet_address,
            'signers': [
                {
                "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
                "weight": 1
                }
            ],
            'xdr': expect_unsigned_xdr,
            'transaction_url': f"{self.host}{reverse('transaction', transaction_hash=expect_tx_hash)}",
            'transaction_hash': expect_tx_hash,
            '@id': url
        }
        assert text == expect

    @unittest_run_loop
    async def test_post_generate_wallet_from_request_json_data_missing(self):
        url = reverse('generate-wallet', wallet_address=self.wallet_address)
        resp = await self.client.request("POST", url)
        assert resp.status == 400
        text = await resp.json()
        assert 'Bad request, JSON data missing.' in text['error']

    @unittest_run_loop
    async def test_post_generate_wallet_from_request_missing_param(self):
        url = reverse('generate-wallet', wallet_address=self.wallet_address)
        resp = await self.client.request("POST", url, json={'target_address':'test', 'amount_xlm':'10'})
        assert resp.status == 400
        text = await resp.json()
        assert text['error'] == 'Parameter \'transaction_source_address\' not found. Please ensure parameters is valid.'

    @unittest_run_loop
    async def test_post_generate_wallet_from_request_use_wrong_parameter(self):
        url = reverse('generate-wallet', wallet_address=self.wallet_address)
        resp = await self.client.request("POST", url, json={'target':'test', 'transaction_source_address': 'test'})
        assert resp.status == 400
        text = await resp.json()
        assert "Parameter 'target_address' not found. Please ensure parameters is valid." in text['error']

        resp = await self.client.request("POST", url, json={
                                         'target_address' : 'test', 'transaction_source_address': 'test',})
        assert resp.status == 400
        text = await resp.json()
        assert 'Balance must have more than 0.' in text['error']

        resp = await self.client.request("POST", url, json={
                                         'target_address' : 'test',
                                         'transaction_source_address': 'test',
                                         'amount_xlm' : 'not_Decimal'})
        assert resp.status == 400
        text = await resp.json()
        assert "not_Decimal is not decimal" in text['error']

    @unittest_run_loop
    @patch('wallet.post_generate_wallet.wallet_address_is_duplicate', **{'return_value' : True})
    async def test_post_generate_wallet_from_request_is_duplicate_wallet_address(self, mock):
        url = reverse('generate-wallet', wallet_address=self.wallet_address)
        json_request = {
            'target_address': self.target_address,
            'transaction_source_address': self.transaction_source_address,
            'amount_xlm': self.amount_xlm
        }

        result = await self.client.request("POST", url, json=json_request)
        assert result.status == 400
        text = await result.json()
        assert 'Target address is already used.' in text['error']

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

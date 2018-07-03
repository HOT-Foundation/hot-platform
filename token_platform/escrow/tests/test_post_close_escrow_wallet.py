import pytest

from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from tests.test_utils import BaseTestClass
from asynctest import patch
from router import reverse
from conf import settings
from decimal import Decimal
# from escrow.post_close_escrow_wallet import (generate_close_escrow_wallet, build_generate_close_escrow_wallet_transaction)

class TestPostCloseEscrowWalletFromRequest(BaseTestClass):
    async def setUpAsync(self):
        self.escrow_address = 'escrow'
        self.provider_address = 'provider'
        self.creator_address = 'creator'
        self.transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        self.tx_hash = 'tx_tash'
        self.unsigned_xdr = 'xdr'
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('escrow.post_close_escrow_wallet.generate_merge_transaction')
    async def test_post_close_escrow_wallet_from_request_success(self, mock_generate_claose_escrow_wallet):

        mock_generate_claose_escrow_wallet.return_value = {
            'wallet_address' : self.escrow_address,
            'transaction_url' : reverse('transaction', transaction_hash=self.tx_hash),
            'signers' : [self.provider_address, self.creator_address],
            'xdr' : self.unsigned_xdr,
            'transaction_hash' : self.tx_hash
        }

        expect = {
            '@id' : reverse('close-escrow-wallet', escrow_address=self.escrow_address),
            'wallet_address' : self.escrow_address,
            'transaction_url' : reverse('transaction', transaction_hash=self.tx_hash),
            'signers' : [self.provider_address, self.creator_address],
            'xdr' : self.unsigned_xdr,
            'transaction_hash' : self.tx_hash
        }

        json = {
            'transaction_source_address': self.transaction_source_address
        }

        url = f"{self.host}{reverse('close-escrow-wallet', escrow_address=self.escrow_address)}"
        resp = await self.client.request('POST', url, json=json)
        assert resp.status == 200
        text = await resp.json()
        assert text == expect


    @unittest_run_loop
    @patch('escrow.post_close_escrow_wallet.generate_merge_transaction')
    async def test_post_close_escrow_wallet_from_request_dont_have_payload(self, mock_generate_claose_escrow_wallet):

        mock_generate_claose_escrow_wallet.return_value = {
            'wallet_address' : self.escrow_address,
            'transaction_url' : reverse('transaction', transaction_hash=self.tx_hash),
            'signers' : [self.provider_address, self.creator_address],
            'xdr' : self.unsigned_xdr,
            'transaction_hash' : self.tx_hash
        }

        url = f"{self.host}{reverse('close-escrow-wallet', escrow_address=self.escrow_address)}"
        resp = await self.client.request('POST', url, json={})
        assert resp.status == 400
        text = await resp.json()
        assert text['message'] == 'Parameter \'transaction_source_address\' not found. Please ensure parameters is valid.'

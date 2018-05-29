from tests.test_utils import BaseTestClass
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from router import reverse
from conf import settings


class TestPostCloseJointWalletFromRequest(BaseTestClass):
    async def setUpAsync(self):
        self.wallet_address = 'wallet_address'
        self.tx_hash = 'tx_hash'
        self.singers = ['singers1', 'singers2']
        self.unsigned_xdr = 'unsigned_xdr'
        self.parties_wallet = {
            'parties' : [
                {'address' : 'wallet1', 'amount' : '15'},
                {'address' : 'wallet2', 'amount' : '20'}
            ]
        }

    @unittest_run_loop
    @patch('joint_wallet.post_close_joint_wallet.generate_merge_transaction')
    async def test_post_cloase_joint_wallet_from_request_success(self, mock_genrate_merge_transaction):

        mock_genrate_merge_transaction.return_value = {
            'wallet_address' : self.wallet_address,
            'transaction_url' : reverse('transaction', transaction_hash=self.tx_hash),
            'signers' : self.singers,
            'xdr' : self.unsigned_xdr,
            'transaction_hash' : self.tx_hash
        }

        expect = {
            '@id' : reverse('close-joint-wallet', wallet_address=self.wallet_address),
            'wallet_address' : self.wallet_address,
            'transaction_url' : reverse('transaction', transaction_hash=self.tx_hash),
            'signers' : self.singers,
            'xdr' : self.unsigned_xdr,
            'transaction_hash' : self.tx_hash
        }

        url = reverse('close-joint-wallet', wallet_address=self.wallet_address)
        resp = self.client.request('POST', url, json=self.parties_wallet)

        assert resp.status == 200
        text = await resp.json()
        assert text == expect



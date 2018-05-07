from tests.test_utils import BaseTestClass
from escrow.get_create_escrow_wallet import get_unsigned_generate_wallet_xdr
from aiohttp.test_utils import unittest_run_loop
from conf import settings

class TestGetUnsignedGenerateWalletXDR(BaseTestClass):

    async def setUpAsync(self):
        self.hotnow_address = 'hotnow'
        self.escrow_address = 'escrow'
        self.merchant_address = 'merchant'
        self.expiration_date = '5/10/45'
        self.cost_per_tx = 50
        self.starting_balance = 500
        self.host = settings['HOST']

    @unittest_run_loop
    async def test_get_unsigned_generate_wallet_xdr(self):
        result = get_unsigned_generate_wallet_xdr(
            stellar_escrow_address=self.escrow_address,
            stellar_merchant_address=self.merchant_address,
            stellar_hotnow_address=self.hotnow_address,
            starting_banace=self.starting_balance,
            exp_date=self.expiration_date,
            cost_per_tx=self.cost_per_tx
            )

        expect = {
            '@id': self.escrow_address,
            '@url': '{}/create-escrow'.format(self.host),
            '@transaction_url': '{}/transaction/{}'.format(self.host, 'tx_hash'),
            'min_signer': 'test2',
            'signers': 3,
            'unsigned_xdr': 'test'
        }

        assert result == expect
    #Create an account.
    #Set options of the account
    #Origin Target
       #Escrow

    #Lock up & Recovery perioding

    #Create account
    ##    Enabling multi sign
     #   Change weiight
     #   Change trust
     #   payment
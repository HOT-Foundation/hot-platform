import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from stellar_base.utils import DecodeError
from tests.test_utils import BaseTestClass

from conf import settings
from wallet.wallet import build_create_wallet_transaction


class TestBuildCreateWalletTx(BaseTestClass):

    async def setUpAsync(self):
        self.source_address = 'GASF2Q2GZMQMMNSYDU34MU4GJKSZPSN7FYKQEMNH4QJMVE3JR3C3I3N5'
        self.destination_address = 'GAL7IFYTLS3KRGLDDN3BO77EE5PL7UPHMWJAAZQXXEBM4LA63UE54HDF'
        self.starting_amount = 500

    class TeMock():
        def hash_meta(self):
            return 'tx-hash'

    class BuilderMock():

        def __init__(self, te):
            self.te = te

        def append_create_account_op(self, source, destination, starting_balance):
            pass

        def append_trust_op(self, source, destination, code):
            if (source == 'decode-error' or destination == 'decode-error'):
                raise DecodeError('decode parameter error')

        def gen_xdr(self):
            return 'unsugned-xdr'

    @unittest_run_loop
    @patch('wallet.wallet.Builder')
    async def test_build_create_wallet_transaction_success(self, mock_builder):
        te = self.TeMock()
        mock_builder.return_value = self.BuilderMock(te)
        actual = build_create_wallet_transaction(
            self.source_address,
            self.destination_address,
            self.starting_amount)
        expect = ('unsugned-xdr', 'tx-hash')
        assert actual == expect


    @unittest_run_loop
    @patch('wallet.wallet.Builder')
    async def test_build_create_wallet_transaction_with_wrong_parameter(self, mock_builder):
        te = self.TeMock()
        mock_builder.return_value = self.BuilderMock(te)
        with pytest.raises(web.HTTPBadRequest):
            build_create_wallet_transaction(
                'decode-error',
                'decode-error',
                self.starting_amount)

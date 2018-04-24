from tests.test_utils import BaseTestClass

import pytest
from aiohttp.test_utils import unittest_run_loop
from aiohttp.web_exceptions import HTTPBadRequest
from asynctest import patch
from transaction.transaction import (get_next_sequence_number, get_signers,
                                     get_threshold_weight,
                                     is_duplicate_transaction,
                                     submit_transaction)
from wallet.tests.factory.wallet import StellarWallet


class TestSubmitTransaction(BaseTestClass):
    @unittest_run_loop
    async def test_submit_transaction_fail_with_duplicate_xdr(self) -> None:
        with pytest.raises(HTTPBadRequest):
            signed_xdr = b'AAAAACRdQ0bLIMY2WB03xlOGSqWXyb8uFQIxp+QSypNpjsW0AAAAZAB79gEAAAAHAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAbUsVq2bqEoCf7vIHxSuFBHDqxrZiYvtyqyavFkpA9wQAAAABDzN9gAAAAAAAAAABaY7FtAAAAEB0OSEaK6FTDW3imY9vU/jFe3dDhz0j5/656Kpns/uzBdSMUvl9q8ZNQes7ASTp98hgsxfZBlVnYAr0jzwY05MI'
            result = await submit_transaction(signed_xdr)

    @unittest_run_loop
    async def test_submit_transaction_fail_with_wrong_xdr(self) -> None:
        with pytest.raises(HTTPBadRequest):
            signed_xdr = b'AAAAACRdQ0bLIMY2WB03xlOGSqWXy'
            result = await submit_transaction(signed_xdr)


class TestDuplicateTransaction(BaseTestClass):

    class TransactionFail():
        def transaction(self, tx_hash):
            return {
                "title": "Resource Missing",
                "status": 404,
                "detail": "The resource at the url requested was not found.  This is usually occurs for one of two reasons:  The url requested is not valid, or no data in our database could be found with the parameters provided."
            }

    class TransactionSuccess():
        def transaction(self, tx_hash):
            return {
                "id": 'testteestsetbbdf'
            }

    @unittest_run_loop
    @patch('transaction.transaction.horizon_livenet')
    @patch('transaction.transaction.horizon_testnet')
    async def test_is_duplicate_transaction_duplicate_when_id_exist(self, mock_test, mock_live) -> None:
        mock_test.return_value = self.TransactionSuccess()
        mock_test.return_value = self.TransactionSuccess()
        tx_hash = 'e11b7a3677fdd45c885e8fb49d0079d083ee8a5cab08e32b00126172abb05111'
        result = await is_duplicate_transaction(tx_hash)
        assert result == True

    @unittest_run_loop
    @patch('transaction.transaction.horizon_livenet')
    @patch('transaction.transaction.horizon_testnet')
    async def test_is_duplicate_transaction_not_duplicate_when_get_not_found(self, mock_test, mock_live) -> None:
        mock_test.return_value = self.TransactionFail()
        mock_live.return_value = self.TransactionFail()
        tx_hash = 'e11b7a3677fdd45c885'
        result = await is_duplicate_transaction(tx_hash)
        assert result == False


class TestGetNextSequenceNumber(BaseTestClass):

    class TransactionSuccess():

        class Account():
            def get(self, str):
                return '1234566789'

        def account(self, wallet_address):
            return self.Account()

    @unittest_run_loop
    @patch('transaction.transaction.horizon_livenet')
    @patch('transaction.transaction.horizon_testnet')
    async def test_get_sequence_number_success(self, mock_test, mock_live) -> None:
        mock_test.return_value = self.TransactionSuccess()
        mock_live.return_value = self.TransactionSuccess()
        wallet_address = 'GASF2Q2GZMQMMNSYDU34MU4GJKSZPSN7FYKQEMNH4QJMVE3JR3C3I3N5'
        result = await get_next_sequence_number(wallet_address)
        assert isinstance(result, str)
        assert result == '1234566789'

class TestGetSigner(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_signers(self, mock_address):
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)

        result = await get_signers('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI')
        expect_result = [{
                'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'weight': 1
            }, {
                'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'weight': 1
            }]
        assert result == expect_result


    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_threshold_weight_low_threshold(self, mock_address):
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)

        result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'allow_trust')
        assert result == 1


    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_threshold_weight_med_threshold(self, mock_address):
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)

        result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'payment')
        assert result == 2


    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_threshold_weight_high_threshold(self, mock_address):
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)

        result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'set_signer')
        assert result == 2

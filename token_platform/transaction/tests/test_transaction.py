import pytest
from aiohttp.test_utils import unittest_run_loop
from aiohttp.web_exceptions import HTTPBadRequest, HTTPInternalServerError
from asynctest import patch
from tests.test_utils import BaseTestClass

from transaction.transaction import (get_current_sequence_number,
                                     is_duplicate_transaction,
                                     submit_transaction)


class TestSubmitTransaction(BaseTestClass):

    class WrongResponse():
        def submit(self, tx_hash):
            raise ValueError('response is not json format.')



    class SuccessTransaction():
        def submit(self, tx_hash):
            return {
                'status': 200,
                'msg' : 'success'
            }

    @unittest_run_loop
    @patch('transaction.transaction.horizon_livenet')
    @patch('transaction.transaction.horizon_testnet')
    async def test_submit_transaction_success(self, mock_test, mock_live) -> None:
        mock_live.return_value = self.SuccessTransaction()
        mock_test.return_value = self.SuccessTransaction()
        signed_xdr = 'Testtest'
        result = await submit_transaction(signed_xdr)
        assert result == mock_test.return_value.submit('test')

    @unittest_run_loop
    async def test_submit_transaction_fail_with_duplicate_xdr(self) -> None:
        with pytest.raises(HTTPBadRequest):
            signed_xdr = b'AAAAACRdQ0bLIMY2WB03xlOGSqWXyb8uFQIxp+QSypNpjsW0AAAAZAB79gEAAAAHAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAbUsVq2bqEoCf7vIHxSuFBHDqxrZiYvtyqyavFkpA9wQAAAABDzN9gAAAAAAAAAABaY7FtAAAAEB0OSEaK6FTDW3imY9vU/jFe3dDhz0j5/656Kpns/uzBdSMUvl9q8ZNQes7ASTp98hgsxfZBlVnYAr0jzwY05MI'
            result = await submit_transaction(signed_xdr)

    @unittest_run_loop
    async def test_submit_transaction_fail_with_wrong_xdr_value(self) -> None:
        with pytest.raises(HTTPBadRequest):
            signed_xdr = b'AAAAACRdQ0bLIMY2WB03xlOGSqWXy'
            result = await submit_transaction(signed_xdr)

    @unittest_run_loop
    @patch('transaction.transaction.horizon_livenet')
    @patch('transaction.transaction.horizon_testnet')
    async def test_submit_transaction_fail_with_wrong_response_format(self, mock_test, mock_live) -> None:
        mock_live.return_value = self.WrongResponse()
        mock_test.return_value = self.WrongResponse()
        with pytest.raises(HTTPInternalServerError):
            signed_xdr = 'Testtest'
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


class TestGetcurrentSequenceNumber(BaseTestClass):

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
        result = await get_current_sequence_number(wallet_address)
        assert isinstance(result, str)
        assert result == '1234566789'

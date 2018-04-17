import pytest
from aiohttp.test_utils import unittest_run_loop
from aiohttp.web_exceptions import HTTPBadRequest
from asynctest import patch
from tests.test_utils import BaseTestClass

from transaction.transaction import submit_transaction, is_duplicate_transaction


class TestSubmitTransactionFromRequest(BaseTestClass):

    @unittest_run_loop
    @patch('transaction.transaction.is_duplicate_transaction')
    @patch('transaction.transaction.submit_transaction')
    async def test_submit_transaction_from_request_success(self, mock_tx, mock_dup) -> None:
        mock_dup.return_value = False
        mock_tx.return_value = {'status': 200}
        url = f'transaction/transaction-hash'
        resp = await self.client.request("PUT", url, data=b'test data')
        assert resp.status == 200
        text = await resp.json()

        expect = {
            'message': 'transaction success.'
        }

        assert text == expect

    @unittest_run_loop
    @patch('transaction.transaction.is_duplicate_transaction')
    @patch('transaction.transaction.submit_transaction')
    async def test_submit_transaction_from_request_error_wrong_parameter(self, mock_tx, mock_dup) -> None:
        mock_dup.return_value = False
        mock_tx.return_value = {'status': 200}
        url = f'transaction/transaction-hash'
        resp = await self.client.request("PUT", url)
        assert resp.status == 400
        text = await resp.json()
        expect = {
            'message': 'transaction fail, please check your parameter.'
        }

        assert text == expect


class TestSubmitTransaction(BaseTestClass):
    @unittest_run_loop
    async def test_submit_transaction_fail(self) -> None:
        with pytest.raises(HTTPBadRequest):
            signed_xdr = b'AAAAACRdQ0bLIMY2WB03xlOGSqWXyb8uFQIxp+QSypNpjsW0AAAAZAB79gEAAAAHAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAbUsVq2bqEoCf7vIHxSuFBHDqxrZiYvtyqyavFkpA9wQAAAABDzN9gAAAAAAAAAABaY7FtAAAAEB0OSEaK6FTDW3imY9vU/jFe3dDhz0j5/656Kpns/uzBdSMUvl9q8ZNQes7ASTp98hgsxfZBlVnYAr0jzwY05MI'
            result = await submit_transaction(signed_xdr)




class TestDuplicateTransaction(BaseTestClass):
    @unittest_run_loop
    async def test_is_duplicate_transaction_success(self) -> None:
        tx_hash = 'e11b7a3677fdd45c885e8fb49d0079d083ee8a5cab08e32b00126172abb05111'
        result = await is_duplicate_transaction(tx_hash)
        assert result == True
        tx_hash = 'e11b7a3677fdd45c885'
        result = await is_duplicate_transaction(tx_hash)
        assert result == False

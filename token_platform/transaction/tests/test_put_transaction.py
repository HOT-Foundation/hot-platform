import pytest
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from tests.test_utils import BaseTestClass


class TestSubmitTransactionFromRequest(BaseTestClass):

    @unittest_run_loop
    @patch('transaction.put_transaction.is_duplicate_transaction')
    @patch('transaction.put_transaction.submit_transaction')
    async def test_put_transaction_from_request_success(self, mock_tx, mock_dup) -> None:
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
    @patch('transaction.put_transaction.is_duplicate_transaction')
    @patch('transaction.put_transaction.submit_transaction')
    async def test_put_transaction_from_request_error_wrong_parameter(self, mock_tx, mock_dup) -> None:
        mock_dup.return_value = False
        mock_tx.return_value = {'status': 200}
        url = f'transaction/transaction-hash'
        resp = await self.client.request("PUT", url)
        assert resp.status == 400
        text = await resp.json()
        expect = {
            'error': 'transaction fail, please check your parameter.'
        }

        assert text == expect

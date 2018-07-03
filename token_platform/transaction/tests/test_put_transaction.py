import pytest
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from tests.test_utils import BaseTestClass
from aiohttp import web
from router import reverse

class TestSubmitTransactionFromRequest(BaseTestClass):

    @unittest_run_loop
    @patch('transaction.put_transaction.is_duplicate_transaction')
    @patch('transaction.put_transaction.submit_transaction')
    async def test_put_transaction_from_request_success(self, mock_tx, mock_dup) -> None:

        mock_dup.return_value = False
        mock_tx.return_value = {'status': 200}
        url = reverse('transaction', transaction_hash='transaction-hash')
        resp = await self.client.request("PUT", url, data=b'test data')
        assert resp.status == 202

    @unittest_run_loop
    @patch('transaction.put_transaction.is_duplicate_transaction')
    @patch('transaction.put_transaction.submit_transaction')
    async def test_put_transaction_from_request_with_no_xdr(self, mock_tx, mock_dup) -> None:
        mock_dup.return_value = False
        mock_tx.return_value = {'status': 200}
        url = reverse('transaction', transaction_hash='transaction-hash')
        resp = await self.client.request("PUT", url)
        assert resp.status == 400
        text = await resp.json()
        assert 'message' in text
        assert 'traceback' in text

    @unittest_run_loop
    @patch('transaction.put_transaction.is_duplicate_transaction')
    @patch('transaction.put_transaction.submit_transaction')
    async def test_put_transaction_from_request_with_duplicate_transaction(self, mock_tx, mock_dup) -> None:
        mock_dup.return_value = True
        mock_tx.return_value = {'status': 200}
        url = reverse('transaction', transaction_hash='transaction-hash')
        resp = await self.client.request("PUT", url, data=b'test data')
        assert resp.status == 400
        text = await resp.json()
        assert 'message' in text
        assert 'traceback' in text

import asyncio
import json

from tests.test_utils import BaseTestClass

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request, unittest_run_loop
from asynctest import patch
from transaction.get_transaction import get_transaction_from_request
from transaction.tests.factory.horizon import HorizonData
from transaction.transaction import get_transaction
from conf import settings
from router import reverse

class TestGetTransactionFromRequest(BaseTestClass):

    @unittest_run_loop
    @patch('transaction.get_transaction.get_transaction')
    async def test_get_transaction_from_request(self, mock_get_transaction) -> None:
        mock_get_transaction.return_value = {}
        tx_hash = '4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9'
        resp = await self.client.request('GET', reverse('transaction', transaction_hash=tx_hash))
        assert resp.status == 200
        mock_get_transaction.assert_called_once_with(tx_hash)


    @unittest_run_loop
    @patch('transaction.transaction.Horizon')
    async def test_get_transaction_success(self, mock_horizon):

        mock_horizon.return_value = HorizonData()

        result = await get_transaction("4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9")
        host = settings.get('HOST', None)
        expect_data = {
            'transaction_id': '4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9',
            '@id': f"{host}{reverse('transaction', transaction_hash='4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9')}",
            'paging_token': '34980756279271424',
            'ledger': 8144592,
            'created_at': '2018-03-28T08:34:22Z',
            'source_account': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
            'source_account_sequence': '33497802856202246',
            'fee_paid': 200,
            'signatures': [
                'Fy+wn01aXyIYbmbnt/lUcqDEElIqeNoISByLRYQYQhB1To23bR32RApsz/QS/zqPFnK75zoNScmDHfGt9AVtBg==',
                'kGrXKXqXdfeY0zkT4YsgZWfoA6j1wD3vmEBvW0hfEOozogG8jpIDqPksgZy16KmFHKYjyQporHsiBx4gqGr9Cg==',
                'kKNbpAx8TzyfHoffKtG1kQKg4x5O+vaa+LQfPh3YQHLK8Z3Tn/1RRPgHI7NxrKzxdxRYCG5AF6ThyllZ6UWsDQ=='
            ],
            'memo': 'memo',
            'operations': [{
                'id': '34980756279271425',
                'paging_token': '34980756279271425',
                'source_account': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'type': 'create_account',
                'type_i': 0,
                'created_at': '2018-03-28T08:34:22Z',
                'transaction_hash': '4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9',
                'starting_balance': '10.0000000',
                'funder': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'account': 'GAULEK4CU7IYZTFVKA4EG3RQLKB7LCSYX2WI46C2KXLDUJGQTSH2JWTD'
            },{'id': '34980756279271430',
                'paging_token': '34980756279271430',
                'source_account': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'type': 'payment',
                'type_i': 1,
                'created_at': '2018-03-28T08:34:22Z',
                'transaction_hash': '4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9',
                'asset_type': 'credit_alphanum4',
                'asset_code': 'HTKN',
                'asset_issuer': 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
                'from': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'to': 'GAULEK4CU7IYZTFVKA4EG3RQLKB7LCSYX2WI46C2KXLDUJGQTSH2JWTD',
                'amount': '20.0000000'
            }]
        }
        assert result == expect_data


    @unittest_run_loop
    @patch('transaction.transaction.Horizon')
    async def test_get_transaction_not_found(self, mock_transaction):
        class MockTransaction(object):
            def transaction(self, tx_hash):
                return {
                    "title": "Resource Missing",
                    "status": 404,
                    "detail": "The resource at the url requested was not found.  This is usually occurs for one of two reasons:  The url requested is not valid, or no data in our database could be found with the parameters provided."
                }

        mock_transaction.return_value = MockTransaction()

        with pytest.raises(web.HTTPNotFound) as context:
            await get_transaction("4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9")
        assert str(context.value) == 'Not Found'


    @unittest_run_loop
    @patch('transaction.get_transaction.get_transaction_by_memo')
    async def test_get_transaction_hash_by_memo_from_reqeust_can_get_tx(self, mock_get_transaction) -> None:
        mock_get_transaction.return_value = {'test': 'test'}
        resp = await self.client.request('GET', reverse('get-transaction-hash-memo', wallet_address='address', memo='hello'))
        assert resp.status == 200
        mock_get_transaction.assert_called_once_with('address', 'hello')
        assert await resp.json() == {'test':'test'}


    @unittest_run_loop
    @patch('transaction.get_transaction.get_transaction_by_memo')
    async def test_get_transaction_hash_by_memo_from_reqeust(self, mock_get_transaction) -> None:
        mock_get_transaction.return_value = {}
        resp = await self.client.request('GET', reverse('get-transaction-hash-memo', wallet_address='address', memo='hello'))
        assert resp.status == 204
        mock_get_transaction.assert_called_once_with('address', 'hello')
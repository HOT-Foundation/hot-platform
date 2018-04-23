from aiohttp import web
from aiohttp.test_utils import make_mocked_request
import asyncio
from asynctest import patch
from transaction.get_transaction import get_transaction_from_request
from transaction.transaction import get_transaction, horizon_testnet
from transaction.tests.factory.horizon import HorizonData
import json
import pytest

@patch('transaction.get_transaction.get_transaction')
async def test_get_transaction_from_request(mock_get_transaction):
    req = make_mocked_request('GET', '/transaction/{}'.format('4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9'),
        match_info={'transaction_hash': '4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9'}
    )
    await get_transaction_from_request(req)
    assert mock_get_transaction.call_count == 1


@asyncio.coroutine
@patch('transaction.transaction.horizon_testnet')
async def test_get_transaction_success(mock_horizon):
    instance = mock_horizon.return_value
    mock_horizon.return_value = HorizonData()

    result = await get_transaction("4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9")

    assert result.status == 200

    actual_data = json.loads(result.text)
    expect_data = {
        '@id': '4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9',
        '@url': 'localhost:8081/transaction/4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9',
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
    assert actual_data == expect_data


@asyncio.coroutine
@patch('transaction.transaction.horizon_testnet')
async def test_get_transaction_not_found(mock_transaction):
    class MockTransaction(object):
        def transaction(self, tx_hash):
            return {
                "title": "Resource Missing",
                "status": 404,
                "detail": "The resource at the url requested was not found.  This is usually occurs for one of two reasons:  The url requested is not valid, or no data in our database could be found with the parameters provided."
            }

    instance = mock_transaction.return_value
    mock_transaction.return_value = MockTransaction()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_transaction("4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9")
    assert str(context.value) == 'Not Found'
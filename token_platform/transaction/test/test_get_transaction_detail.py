from aiohttp.test_utils import make_mocked_request
from transaction.get_transaction import get_transaction_from_request
from asynctest import patch


@patch('transaction.get_transaction.get_transaction')
async def test_get_transaction_from_request(mock_get_transaction):
    req = make_mocked_request('GET', '/transaction/{}'.format('4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9'),
        match_info={'tx_hash': '4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9'}
    )
    await get_transaction_from_request(req)
    assert mock_get_transaction.call_count == 1
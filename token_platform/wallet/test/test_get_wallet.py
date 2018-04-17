import pytest
from aiohttp import web
import asyncio
from router import routes
from asynctest import patch
from wallet.get_wallet import get_wallet, StellarAddress, get_wallet_from_request
from aiohttp.test_utils import make_mocked_request
import json
from stellar_base.utils import AccountNotExistError
from wallet.test.factory.wallet import StellarWallet
from conf import settings

@patch('wallet.get_wallet.get_wallet')
async def test_get_wallet_from_request(mock_get_wallet):
    req = make_mocked_request('GET', '/wallet/{}'.format('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'),
        match_info={'wallet_address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'}
    )
    await get_wallet_from_request(req)
    assert mock_get_wallet.call_count == 1


@asyncio.coroutine
@patch('wallet.get_wallet.StellarAddress')
async def test_get_wallet_success_trusted_htkn(mock_address):
    instance = mock_address.return_value
    balances =[{
        'balance': '7.0000000',
        'limit': '922337203685.4775807',
        'asset_type': 'credit_alphanum4',
        'asset_code': 'HTKN',
        'asset_issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
    },
    {
        'balance': '9.9999200',
        'asset_type': 'native'
    }]
    mock_address.return_value = StellarWallet(balances)

    result = await get_wallet('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')

    assert result.status == 200

    actual_data = json.loads(result.text)
    expect_data = {
        '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@url': 'localhost:8081/wallet/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'asset': {
            'HTKN': '7.0000000',
            'XLM': '9.9999200'
        }
    }
    assert actual_data == expect_data


@asyncio.coroutine
@patch('wallet.get_wallet.StellarAddress')
async def test_get_wallet_success_not_trust_htkn(mock_address):
    instance = mock_address.return_value
    balances =[
    {
        'balance': '9.9999200',
        'asset_type': 'native'
    }]
    mock_address.return_value = StellarWallet(balances)

    result = await get_wallet('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')

    assert result.status == 200

    actual_data = json.loads(result.text)
    expect_data = {
        '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@url': 'localhost:8081/wallet/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'trust': '{}/wallet/{}/transaction/change-trust'.format(settings['HOST'], 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'),
        'asset': {
            'XLM': '9.9999200'
        }
    }
    assert actual_data == expect_data


@asyncio.coroutine
@patch('wallet.get_wallet.StellarAddress')
async def test_get_wallet_not_found(mock_address):
    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    instance = mock_address.return_value
    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet('GB7D54NKPWYYMMS7JFEQZKDDTW5R7IMXTFN2WIEST2YZVVNO3SHJ3Y7M')
    assert str(context.value) == 'Not Found'


@asyncio.coroutine
@patch('wallet.get_wallet.StellarAddress')
async def test_get_wallet_invalid_address(mock_address):
    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    instance = mock_address.return_value
    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet('XXXX')
    assert str(context.value) == 'Not Found'

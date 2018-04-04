import pytest
from aiohttp import web
import asyncio
from router import routes
from asynctest import patch
from wallet.get_wallet import get_wallet, stellar_address, format_signers, map_balance, format_balance, get_wallet_from_request
from aiohttp.test_utils import make_mocked_request
import json
from stellar_base.utils import AccountNotExistError
from wallet.test.factory.wallet import StellarWallet, BALANCES, SIGNERS, WALLET


async def test_get_wallet_from_request():
    req = make_mocked_request('GET', '/wallet/{}'.format('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'),
        match_info={'wallet_address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'}
    )
    result = await get_wallet_from_request(req)
    assert result == WALLET


@asyncio.coroutine
@patch('wallet.get_wallet.stellar_address')
async def xtest_get_wallet_success(mock_address):
    instance = mock_address.return_value
    mock_address.return_value = StellarWallet()

    req = make_mocked_request('GET', '/wallet/{}'.format('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'),
        match_info={'wallet_address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'}
    )
    result = await get_wallet(req)

    assert result.status == 200

    actual_data = json.loads(result.text)

    assert actual_data == WALLET


@asyncio.coroutine
@patch('wallet.get_wallet.stellar_address')
async def xtest_get_wallet_not_found(mock_address):
    resp = make_mocked_request('GET', '/wallet/{}'.format('GB7D54NKPWYYMMS7JFEQZKDDTW5R7IMXTFN2WIEST2YZVVNO3SHJ3Y7M'),
        match_info={'wallet_address': 'GB7D54NKPWYYMMS7JFEQZKDDTW5R7IMXTFN2WIEST2YZVVNO3SHJ3Y7M'}
    )

    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    instance = mock_address.return_value
    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet(resp)
    assert str(context.value) == 'Not Found'


@asyncio.coroutine
@patch('wallet.get_wallet.stellar_address')
async def xtest_get_wallet_invalid_address(mock_address):
    resp = make_mocked_request('GET', '/wallet/{}'.format('XXXX'),
        match_info={'wallet_address': 'XXXX'}
    )

    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    instance = mock_address.return_value
    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet(resp)
    assert str(context.value) == 'Not Found'


def test_format_signer():
    signer = SIGNERS[0]
    format_signers(signer)
    assert signer == {
            'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
            'weight': 1,
            'type': 'ed25519_public_key'
        }


def test_map_balance():

    result = map_balance(BALANCES)

    assert result == {
        'RNTK': {
            'balance': '7.0000000',
            'issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
        },
        'XLM': {
            'balance': '9.9999200',
            'issuer': 'native'
        }
    }


def test_map_empty_balance():
    balances = []
    with pytest.raises(TypeError) as context:
        map_balance(balances)
    assert str(context.value) == 'reduce() of empty sequence with no initial value'


def test_format_balance_asset_type_native():
    balance = {
        'balance': '9.9999200',
        'asset_type': 'native'
    }
    result = format_balance(balance)
    assert result == {'XLM': {'balance': '9.9999200', 'issuer': 'native'}}


def test_format_balance_asset_type_not_native():
    balance = {
        'balance': '7.0000000',
        'limit': '922337203685.4775807',
        'asset_type': 'credit_alphanum4',
        'asset_code': 'RNTK',
        'asset_issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
    }
    result = format_balance(balance)
    assert result == {'RNTK': {'balance': '7.0000000', 'issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'}}

import pytest
from aiohttp import web
import asyncio
from router import routes
from asynctest import patch
from wallet.get_wallet import get_wallet, stellar_address, format_signers, map_balance, get_wallet_from_request, wallet_response
from aiohttp.test_utils import make_mocked_request
import json
from stellar_base.utils import AccountNotExistError
from wallet.test.factory.wallet import StellarWallet

@patch('wallet.get_wallet.get_wallet')
async def test_get_wallet_from_request(mock_get_wallet):
    req = make_mocked_request('GET', '/wallet/{}'.format('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'),
        match_info={'wallet_address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'}
    )
    await get_wallet_from_request(req)
    assert mock_get_wallet.call_count == 1


@asyncio.coroutine
@patch('wallet.get_wallet.stellar_address')
async def test_get_wallet_success(mock_address):
    instance = mock_address.return_value
    mock_address.return_value = StellarWallet()

    result = await get_wallet('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')

    assert result.status == 200

    actual_data = json.loads(result.text)
    expect_data = wallet_response(
        'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD', 
        {
            'HTKN': {
                'balance': '7.0000000',
                'issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
            },
            'XLM': {
                'balance': '9.9999200',
                'issuer': 'native'
            }
        }, 
        {
            'low_threshold': 1,
            'med_threshold': 2,
            'high_threshold': 2
        }, 
        [{
            'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
            'weight': 1,
            'type': 'ed25519_public_key'
        },
        {
            'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
            'weight': 1,
            'type': 'ed25519_public_key'
        },
        {
            'public_key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
            'weight': 0,
            'type': 'ed25519_public_key'
        }])
    assert actual_data == expect_data


@asyncio.coroutine
@patch('wallet.get_wallet.stellar_address')
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
@patch('wallet.get_wallet.stellar_address')
async def test_get_wallet_invalid_address(mock_address):
    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    instance = mock_address.return_value
    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet('XXXX')
    assert str(context.value) == 'Not Found'


def test_format_signer():
    result = format_signers(StellarWallet().signers)
    assert result == [{
        'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
        'weight': 1,
        'type': 'ed25519_public_key'
    },
    {
        'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
        'weight': 1,
        'type': 'ed25519_public_key'
    },
    {
        'public_key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'weight': 0,
        'type': 'ed25519_public_key'
    }]


def test_map_balance():
    result = map_balance(StellarWallet().balances)
    assert result == {
        'HTKN': {
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


def xtest_format_balance_asset_type_native():
    balance = {
        'balance': '9.9999200',
        'asset_type': 'native'
    }
    result = format_balance(balance)
    assert result == {'XLM': {'balance': '9.9999200', 'issuer': 'native'}}


def xtest_format_balance_asset_type_not_native():
    balance = {
        'balance': '7.0000000',
        'limit': '922337203685.4775807',
        'asset_type': 'credit_alphanum4',
        'asset_code': 'HTKN',
        'asset_issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
    }
    result = format_balance(balance)
    assert result == {'HTKN': {'balance': '7.0000000', 'issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'}}

def test_wallet_response():
    actual_data = wallet_response(
        'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        {
            'HTKN': {
                'balance': '7.0000000',
                'issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
            },
            'XLM': {
                'balance': '9.9999200',
                'issuer': 'native'
            }
        },
        {
            'low_threshold': 1,
            'med_threshold': 2,
            'high_threshold': 2
        },
        [{
            'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
            'weight': 1,
            'type': 'ed25519_public_key'
        },
        {
            'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
            'weight': 1,
            'type': 'ed25519_public_key'
        },
        {
            'public_key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
            'weight': 0,
            'type': 'ed25519_public_key'
        }]
    )
    expect_data = {
        '@url': 'localhost:8081/wallet/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'asset': {
            'HTKN': {
                'balance': '7.0000000',
                'issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
            },
            'XLM': {
                'balance': '9.9999200',
                'issuer': 'native'
            }
        },
        'thresholds': {
            'low_threshold': 1,
            'med_threshold': 2,
            'high_threshold': 2
        },
        'signers': [
            {
                'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'weight': 1,
                'type': 'ed25519_public_key'
            }, {
                'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'weight': 1,
                'type': 'ed25519_public_key'
            }, {
                'public_key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
                'weight': 0,
                'type': 'ed25519_public_key'
            }
        ]
    }

    assert actual_data == expect_data
import pytest
from aiohttp import web
import asyncio
from router import routes
from asynctest import patch
from account.get_account import get_account, Address, format_signers, map_balance, format_balance
from aiohttp.test_utils import make_mocked_request
import json
from stellar_base.utils import AccountNotExistError


@asyncio.coroutine
@patch('account.get_account.Address')
async def test_get_account_success(mock_address):
    instance = mock_address.return_value
    mock_data = {
        'address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'sequence': '33880235334172680',
        'balances': [
            {
                'balance': '7.0000000',
                'limit': '922337203685.4775807',
                'asset_type': 'credit_alphanum4',
                'asset_code': 'RNTK',
                'asset_issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
            },
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }
        ],
        'paging_token': '',
        'thresholds': {
            'low_threshold': 1,
            'med_threshold': 2,
            'high_threshold': 2
        },
        'signers': [
            {
                'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'weight': 1,
                'key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'type': 'ed25519_public_key'
            },
            {
                'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'weight': 1,
                'key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'type': 'ed25519_public_key'
            },
            {
                'public_key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
                'weight': 0,
                'key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
                'type': 'ed25519_public_key'
            }
        ],
        'data': {}
    }
    class MockAddress(object):
        def get(self):
            pass

        @property
        def balances(self):
            return mock_data['balances']

        @property
        def signers(self):
            return mock_data['signers']

        @property
        def thresholds(self):
            return mock_data['thresholds']

    mock_address.return_value = MockAddress()

    req = make_mocked_request('GET', '/account/{}'.format('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'),
        match_info={'account_address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'}
    )
    result = await get_account(req)

    assert result.status == 200

    actual_data = json.loads(result.text)
    expect_data = {
        '@url': 'localhost:8081/account/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'asset': {
            'RNTK': {
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


@asyncio.coroutine
@patch('account.get_account.Address')
async def test_get_account_not_found(mock_address):
    resp = make_mocked_request('GET', '/account/{}'.format('GB7D54NKPWYYMMS7JFEQZKDDTW5R7IMXTFN2WIEST2YZVVNO3SHJ3Y7M'),
        match_info={'account_address': 'GB7D54NKPWYYMMS7JFEQZKDDTW5R7IMXTFN2WIEST2YZVVNO3SHJ3Y7M'}
    )

    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    instance = mock_address.return_value
    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_account(resp)
    assert str(context.value) == 'Not Found'


@asyncio.coroutine
@patch('account.get_account.Address')
async def test_get_account_invalid_address(mock_address):
    resp = make_mocked_request('GET', '/account/{}'.format('XXXX'),
        match_info={'account_address': 'XXXX'}
    )

    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    instance = mock_address.return_value
    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_account(resp)
    assert str(context.value) == 'Not Found'


def test_format_signer():
    signer = {
        'key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
        'weight': 1,
        'type': 'ed25519_public_key'
    }
    format_signers(signer)
    assert signer == {
            'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
            'weight': 1,
            'type': 'ed25519_public_key'
        }


def test_map_balance():
    balances = [
        {
            'balance': '7.0000000',
            'limit': '922337203685.4775807',
            'asset_type': 'credit_alphanum4',
            'asset_code': 'RNTK',
            'asset_issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
        },
        {
            'balance': '9.9999200',
            'asset_type': 'native'
        }
    ]
    result = map_balance(balances)

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

import asyncio

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from asynctest import patch
from stellar_base.exceptions import AccountNotExistError

from conf import settings
from wallet.wallet import StellarAddress, get_wallet
from wallet.get_wallet import (get_wallet_detail,
                               get_wallet_from_request)
from wallet.tests.factory.wallet import StellarWallet
from router import reverse


@patch('wallet.get_wallet.get_wallet_detail')
async def test_get_wallet_from_request(mock_get_wallet):
    mock_get_wallet.return_value = {}
    wallet_address = 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'
    req = make_mocked_request('GET', reverse('wallet-address', wallet_address=wallet_address),
                              match_info={'wallet_address': wallet_address})
    await get_wallet_from_request(req)
    assert mock_get_wallet.call_count == 1


@asyncio.coroutine
@patch('wallet.get_wallet.get_wallet')
async def test_get_wallet_success_trusted_htkn(mock_address):

    balances = [{
        'balance': '7.0000000',
        'limit': '922337203685.4775807',
        'asset_type': 'credit_alphanum4',
        'asset_code': 'HTKN',
        'asset_issuer': 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
    },{
        'balance': '10.0000000',
        'limit': '1000',
        'asset_type': 'credit_alphanum4',
        'asset_code': 'PTKN',
        'asset_issuer': 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
    },{
        'balance': '9.9999200',
        'asset_type': 'native'
    }]
    mock_address.return_value = StellarWallet(balances)

    result = await get_wallet_detail('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')

    host = settings.get('HOST', None)
    url = reverse('wallet-address', wallet_address='GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')
    expect_data = {
        'wallet_address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@id': f'{host}{url}',
        'asset': {
            'HTKN': '7.0000000',
            'XLM': '9.9999200'
        },
        'sequence': '1',
        'data': {
            'age': '30',
            'name': 'UnitTest'
        }
    }
    assert result == expect_data


@asyncio.coroutine
@patch('wallet.get_wallet.get_wallet')
async def test_get_wallet_success_not_trust_htkn(mock_address):

    balances = [
        {
            'balance': '9.9999200',
            'asset_type': 'native'
        }]
    mock_address.return_value = StellarWallet(balances)

    result = await get_wallet_detail('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')

    host = host = settings.get('HOST', None)
    url = reverse('wallet-address', wallet_address='GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')
    expect_data = {
        'wallet_address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@id': f'{host}{url}',
        'trust': f"{settings['HOST']}{reverse('change-trust', wallet_address='GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')}",
        'asset': {
            'XLM': '9.9999200'
        },
        'sequence': '1',
        'data': {
            'age': '30',
            'name': 'UnitTest'
        }
    }
    assert result == expect_data


@asyncio.coroutine
@patch('wallet.wallet.StellarAddress')
async def test_get_wallet_success(mock_address):

    balances = [
        {
            'balance': '9.9999200',
            'asset_type': 'native'
        }]
    mock_address.return_value = StellarWallet(balances)

    result = await get_wallet('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')
    expect_result = {
        "address": "GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD",
        "balances": [
            {
            "balance": "9.9999200",
            "asset_type": "native"
            }
        ],
        "signers": [
            {
            "public_key": "GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF",
            "weight": 1,
            "key": "GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF",
            "type": "ed25519_public_key"
            },
            {
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "weight": 1,
            "key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "type": "ed25519_public_key"
            },
            {
            "public_key": "GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD",
            "weight": 0,
            "key": "GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD",
            "type": "ed25519_public_key"
            }
        ],
        "thresholds": {
            "low_threshold": 1,
            "med_threshold": 2,
            "high_threshold": 2
        },
        "data": {
            "name": "VW5pdFRlc3Q=",
            "age": "MzA="
        },
        "sequence": "1"
    }
    assert result.__dict__ == expect_result


@asyncio.coroutine
@patch('wallet.wallet.StellarAddress')
async def test_get_wallet_not_found(mock_address):
    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet_detail('GB7D54NKPWYYMMS7JFEQZKDDTW5R7IMXTFN2WIEST2YZVVNO3SHJ3Y7M')
    assert str(context.value) == 'Resource Missing: GB7D54NKPWYYMMS7JFEQZKDDTW5R7IMXTFN2WIEST2YZVVNO3SHJ3Y7M'


@asyncio.coroutine
@patch('wallet.wallet.StellarAddress')
async def test_get_wallet_invalid_address(mock_address):
    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet_detail('XXXX')
    assert str(context.value) == 'Resource Missing: XXXX'

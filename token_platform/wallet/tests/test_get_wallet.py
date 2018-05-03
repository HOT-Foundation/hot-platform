import asyncio
import json

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from asynctest import patch
from stellar_base.utils import AccountNotExistError

from conf import settings
from router import routes
from wallet.wallet import StellarAddress, get_wallet
from wallet.get_wallet import (get_wallet_detail,
                               get_wallet_from_request)
from wallet.tests.factory.wallet import StellarWallet


@patch('wallet.get_wallet.get_wallet_detail')
async def test_get_wallet_from_request(mock_get_wallet):
    wallet_address = 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'
    req = make_mocked_request('GET', '/wallet/{}'.format(wallet_address),
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

    assert result.status == 200

    actual_data = json.loads(result.text)
    host = settings.get('HOST', None)
    expect_data = {
        '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@url': f'{host}/wallet/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'asset': {
            'HTKN': '7.0000000',
            'XLM': '9.9999200'
        }
    }
    assert actual_data == expect_data


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

    assert result.status == 200

    actual_data = json.loads(result.text)
    host = host = settings.get('HOST', None)
    expect_data = {
        '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@url': f'{host}/wallet/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'trust': '{}/wallet/{}/transaction/change-trust'.format(settings['HOST'], 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'),
        'asset': {
            'XLM': '9.9999200'
        }
    }
    assert actual_data == expect_data


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
        "id": "GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD",
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
            "name": "UnitTest"
        }
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
    assert str(context.value) == 'Not Found'


@asyncio.coroutine
@patch('wallet.wallet.StellarAddress')
async def test_get_wallet_invalid_address(mock_address):
    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet_detail('XXXX')
    assert str(context.value) == 'Not Found'

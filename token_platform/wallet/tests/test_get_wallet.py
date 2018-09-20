import asyncio

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from asynctest import patch
from stellar_base.exceptions import AccountNotExistError, HorizonError

from conf import settings
from wallet.wallet import get_wallet
from wallet.get_wallet import get_wallet_detail, get_wallet_from_request
from wallet.tests.factory.wallet import StellarWallet
from router import reverse
from stellar.wallet import Wallet


@patch('wallet.get_wallet.get_wallet_detail')
async def test_get_wallet_from_request(mock_get_wallet):
    mock_get_wallet.return_value = {}
    wallet_address = 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'
    req = make_mocked_request(
        'GET', reverse('wallet-address', wallet_address=wallet_address), match_info={'wallet_address': wallet_address}
    )
    await get_wallet_from_request(req)
    assert mock_get_wallet.call_count == 1


@asyncio.coroutine
@patch('wallet.get_wallet.get_wallet')
async def test_get_wallet_success_trusted_htkn(mock_address):

    balances = [
        {
            'balance': '7.0000000',
            'limit': '922337203685.4775807',
            'asset_type': 'credit_alphanum4',
            'asset_code': 'HOT',
            'asset_issuer': 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
        },
        {
            'balance': '10.0000000',
            'limit': '1000',
            'asset_type': 'credit_alphanum4',
            'asset_code': 'PTKN',
            'asset_issuer': 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
        },
        {'balance': '9.9999200', 'asset_type': 'native'},
    ]
    mock_address.return_value = StellarWallet(balances)

    result = await get_wallet_detail('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')

    host = settings.get('HOST', None)
    url = reverse('wallet-address', wallet_address='GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')
    expect_data = {
        'wallet_address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@id': f'{host}{url}',
        'asset': {'HOT': '7.0000000', 'XLM': '9.9999200'},
        'sequence': '1',
        'data': {'age': '30', 'name': 'UnitTest'},
    }
    assert result == expect_data


@asyncio.coroutine
@patch('wallet.get_wallet.get_wallet')
async def test_get_wallet_success_not_trust_htkn(mock_address):

    balances = [{'balance': '9.9999200', 'asset_type': 'native'}]
    mock_address.return_value = StellarWallet(balances)

    result = await get_wallet_detail('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')

    host = host = settings.get('HOST', None)
    url = reverse('wallet-address', wallet_address='GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')
    expect_data = {
        'wallet_address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@id': f'{host}{url}',
        'trust': f"{settings['HOST']}{reverse('change-trust-add-token', wallet_address='GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')}",
        'asset': {'XLM': '9.9999200'},
        'sequence': '1',
        'data': {'age': '30', 'name': 'UnitTest'},
    }
    assert result == expect_data


@asyncio.coroutine
@patch('wallet.wallet.get_stellar_wallet')
async def test_get_wallet_success(mock_address):
    address = 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'
    balances = [{'balance': '9.9999200', 'asset_type': 'native'}]
    sequence = 1
    data = {"name": "VW5pdFRlc3Q=", "age": "MzA="}
    thresholds = {"low_threshold": 1, "med_threshold": 2, "high_threshold": 2}
    signers = [
        {
            "public_key": "GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF",
            "weight": 1,
            "key": "GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF",
            "type": "ed25519_public_key",
        }
    ]

    mock_address.return_value = Wallet(address, balances, sequence, data, signers, thresholds, {})

    result = await get_wallet(address)
    expect_result = {
        "address": address,
        "balances": balances,
        "signers": signers,
        "thresholds": thresholds,
        "data": data,
        "sequence": sequence,
        "flags": {},
    }
    assert result.__dict__ == expect_result


@asyncio.coroutine
@patch('wallet.wallet.get_wallet')
async def test_get_wallet_not_found(mock_address):
    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet_detail('YYYY')
    assert (
        str(context.value)
        == 'The resource at the url requested was not found.  This is usually occurs for one of two reasons:  The url requested is not valid, or no data in our database could be found with the parameters provided.: YYYY'
    )


@asyncio.coroutine
@patch('wallet.wallet.get_wallet')
async def test_get_wallet_invalid_address(mock_address):
    with pytest.raises(web.HTTPNotFound) as context:
        await get_wallet_detail('XXXX')
    assert (
        str(context.value)
        == 'The resource at the url requested was not found.  This is usually occurs for one of two reasons:  The url requested is not valid, or no data in our database could be found with the parameters provided.: XXXX'
    )

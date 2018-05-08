import asyncio
import json

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from asynctest import patch
from stellar_base.utils import AccountNotExistError

from conf import settings
from escrow.get_escrow_wallet import (get_escrow_wallet_detail,
                                      get_escrow_wallet_from_request)
from router import routes
from wallet.tests.factory.wallet import StellarWallet
from wallet.wallet import StellarAddress, get_wallet


@patch('escrow.get_escrow_wallet.get_escrow_wallet_detail')
async def test_get_escrow_wallet_from_request(mock_get_escrow_wallet):
    mock_get_escrow_wallet.return_value = {'account': 'yes'}
    wallet_address = 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'
    req = make_mocked_request('GET', '/escrow/{}'.format(wallet_address),
                              match_info={'wallet_address': wallet_address})
    await get_escrow_wallet_from_request(req)
    assert mock_get_escrow_wallet.call_count == 1


@asyncio.coroutine
@patch('escrow.get_escrow_wallet.get_wallet')
async def test_get_escrow_wallet_success_trusted_htkn(mock_address):

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

    actual_data = await get_escrow_wallet_detail('GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')
    host = settings.get('HOST', None)
    expect_data = {
        '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@url': f'{host}/escrow/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'asset': {
            'HTKN': '7.0000000',
            'XLM': '9.9999200'
        },
        'generate-wallet': f'{host}/escrow/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD/generate-wallet',
        'data': {
            'name': 'UnitTest',
            'age': '30'
        }
    }
    assert actual_data == expect_data


@asyncio.coroutine
@patch('wallet.wallet.StellarAddress')
async def test_get_escrow_wallet_not_found(mock_address):
    class MockAddress(object):
        def get(self):
            raise AccountNotExistError('Resource Missing')

    mock_address.return_value = MockAddress()

    with pytest.raises(web.HTTPNotFound) as context:
        await get_escrow_wallet_detail('GB7D54NKPWYYMMS7JFEQZKDDTW5R7IMXTFN2WIEST2YZVVNO3SHJ3Y7M')
    assert str(context.value) == 'Resource Missing: GB7D54NKPWYYMMS7JFEQZKDDTW5R7IMXTFN2WIEST2YZVVNO3SHJ3Y7M'
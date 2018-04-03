import pytest
from aiohttp import web
import asyncio
from router import routes

from unittest.mock import patch
from account.get_account import get_account, Address
from utils.nametuple_mapping import map_namedtuple

async def xtest_call_get_account(cli):
    with patch.object(Address, 'get') as mock_address:
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

        mock_address.return_value = map_namedtuple(mock_data)
        result = await cli.get('/account/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')
        json = await result.json()
        assert json == {}


async def test_get_account_success(cli):
    resp = await cli.get('/account/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD')
    assert resp.status == 200
    actual = await resp.json()
    expect = {
        "asset": {
            "RNTK": {
                "balance": "7.0000000",
                "issuer": "GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD"
            },
            "XLM": {
                "balance": "9.9999200",
                "issuer": "native"
            }
        },
        "thresholds": {
            "low_threshold": 1,
            "med_threshold": 2,
            "high_threshold": 2,
        },
        "signers": [{
            "public_key": "GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF",
            "type": "ed25519_public_key",
            "weight": 1,
        }, {
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "type": "ed25519_public_key",
            "weight": 1,
        }, {
            "public_key": "GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD",
            "type": "ed25519_public_key",
            "weight": 0,
        }],
        "@id": "GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD",
        "@url": "localhost:8080/account/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD"
    }
    assert actual == expect


async def test_get_account_not_found(cli):
    resp = await cli.get('/account/GC7PF4PSLSLQKPMUS54H4F5WWT7KB5S7OWAI2Q7QG2BNNXF4FBEWVJOG')
    assert resp.status == 404
    actual = await resp.json()
    expect = {'error': 'Resource Missing'}
    assert actual == expect


async def test_get_account_invalid_address(cli):
    resp = await cli.get('/account/XXXX')
    assert resp.status == 404
    actual = await resp.json()
    expect = {'error': 'Resource Missing'}
    assert actual == expect
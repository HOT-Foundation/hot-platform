from aiohttp import web
from stellar_base.address import Address
from pprint import pprint


async def get_account(request):
    account_address = request.match_info.get('account_address', "")
    account = Address(address=account_address)
    account.get()

    # {'address': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
    #  'balances': [{'asset_code': 'RNTK',
    #                'asset_issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD',
    #                'asset_type': 'credit_alphanum4',
    #                'balance': '7.0000000',
    #                'limit': '922337203685.4775807'},
    #               {'asset_type': 'native', 'balance': '9.9999200'}],
    #  'data': {},
    #  'flags': {'auth_required': False, 'auth_revocable': False},
    #  'horizon': <stellar_base.horizon.Horizon object at 0x7f0ecfe32550>,
    #  'network': 'TESTNET',
    #  'paging_token': '',
    #  'secret': None,
    #  'sequence': '33880235334172680',
    #  'signers': [{'key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
    #               'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
    #               'type': 'ed25519_public_key',
    #               'weight': 1},
    #              {'key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
    #               'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
    #               'type': 'ed25519_public_key',
    #               'weight': 1},
    #              {'key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
    #               'public_key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
    #               'type': 'ed25519_public_key',
    #               'weight': 0}],
    #  'thresholds': {'high_threshold': 2, 'low_threshold': 1, 'med_threshold': 2}}

    result = {
        "asset": {
            "HTKN": {
                "balance": "100.0000000",
                "issuer": "GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD"
            },
            "XLM": {
                "balance": "5.0000000",
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

    return web.json_response(result)
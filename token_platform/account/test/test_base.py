import pytest
from aiohttp import web
import asyncio
from router import routes


@pytest.fixture
def cli(loop, aiohttp_client):
    app = web.Application()
    app.add_routes(routes)
    return loop.run_until_complete(aiohttp_client(app))

async def test_case_001(cli):
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


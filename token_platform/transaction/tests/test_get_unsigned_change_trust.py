import asyncio
import json

import pytest
from aiohttp.test_utils import make_mocked_request
from asynctest import patch
from transaction.get_unsigned_change_trust import (get_signers,
                                               get_threshold_weight,
                                               get_unsigned_change_trust,
                                               get_unsigned_change_trust_from_request)
from wallet.tests.factory.wallet import StellarWallet


@patch('transaction.get_unsigned_change_trust.get_unsigned_change_trust')
async def test_get_transaction_from_request(mock_get_unsigned_change_trust):
    req = make_mocked_request('GET', '/wallet/{}/transaction/change-trust'.format('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'),
        match_info={'wallet_address': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'}
    )
    await get_unsigned_change_trust_from_request(req)
    assert mock_get_unsigned_change_trust.call_count == 1

@asyncio.coroutine
@patch('transaction.get_unsigned_change_trust.get_signers')
@patch('transaction.get_unsigned_change_trust.get_threshold_weight')
async def test_get_unsigned_change_trust(mock_get_threshold_weight, mock_get_signer):
    mock_get_threshold_weight.return_value = 1
    mock_get_signer.return_value = [{
        "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
        "weight": 1
    }]

    result = await get_unsigned_change_trust(
        'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI')
    assert result.status == 200
    expect_data = {
        "@id": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
        "@url": "localhost:8081/wallet/GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI/transaction/change-trust",
        "@transaction_url": "localhost:8081/transaction/facf1e0e9060fcbdbaafe9d2d6f29a25b6ae8bae5dc9273feab02b803638cf47",
        "min_signer": 1,
        "signers": [
            {
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "weight": 1
            }
        ],
        "unsigned_xdr": "AAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAZAB3A5sAAAAGAAAAAAAAAAAAAAABAAAAAQAAAADOf93UUiwNNmwwYj2/XOv/KuhgA2mooc0ID+GYa49siQAAAAYAAAABSFRLTgAAAADkHacjwpeFWz5txveZ4sJ3pEmTzpdS9fiBscDwpmoppgAAAASoF8gAAAAAAAAAAAA="
    }

    assert json.loads(result.text) == expect_data
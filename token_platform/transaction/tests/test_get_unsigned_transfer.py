import asyncio
import json

import pytest
from aiohttp.test_utils import make_mocked_request
from asynctest import patch
from transaction.get_unsigned_transfer import (get_signers,
                                               get_threshold_weight,
                                               get_unsigned_transfer,
                                               get_unsigned_transfer_from_request)
from wallet.tests.factory.wallet import StellarWallet


@patch('transaction.get_unsigned_transfer.get_unsigned_transfer')
async def test_get_transaction_from_request(mock_get_unsigned_transfer):
    req = make_mocked_request('GET', '/wallet/{}/transaction/transfer?destination=GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6&amount=100'.format('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'),
        match_info={'wallet_address': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'}
    )
    await get_unsigned_transfer_from_request(req)
    assert mock_get_unsigned_transfer.call_count == 1


@patch('transaction.get_unsigned_transfer.get_unsigned_transfer')
async def test_get_transaction_from_request_invalid_query(mock_get_unsigned_transfer):
    req = make_mocked_request('GET', '/wallet/{}/transaction/transfer?des=GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6&amount=100'.format('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'),
        match_info={'wallet_address': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'}
    )

    with pytest.raises(ValueError) as context:
        await get_unsigned_transfer_from_request(req)
    assert str(context.value) == 'Invalid, please check your parameter.'


@asyncio.coroutine
@patch('transaction.get_unsigned_transfer.get_signers')
@patch('transaction.get_unsigned_transfer.get_threshold_weight')
async def test_get_unsigned_transfer(mock_get_threshold_weight, mock_get_signer):
    mock_get_threshold_weight.return_value = 1
    mock_get_signer.return_value = [{
        "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
        "weight": 1
    }]

    result = await get_unsigned_transfer(
        'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
        'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6',
        100)
    assert result.status == 200
    expect_data = {
        "@id": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
        "@url": "localhost:8081/wallet/GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI/transaction/transfer",
        "@transaction_url": "localhost:8081/transaction/d35077598b9fd20083201d570d779bccba02922e0e7556f698961c242f0ba9ff",
        "min_signer": 1,
        "signers": [
            {
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "weight": 1
            }
        ],
        "unsigned_xdr": "AAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAZAB3A5sAAAAFAAAAAAAAAAAAAAABAAAAAQAAAADOf93UUiwNNmwwYj2/XOv/KuhgA2mooc0ID+GYa49siQAAAAEAAAAA2ZlGnrw2xRHbxWDQCoRQRz8b/Ua+KYUBVdlcf4Ec5bEAAAABSFRLTgAAAADkHacjwpeFWz5txveZ4sJ3pEmTzpdS9fiBscDwpmoppgAAAAA7msoAAAAAAAAAAAA="
    }
    assert json.loads(result.text) == expect_data
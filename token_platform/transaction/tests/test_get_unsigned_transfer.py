import asyncio
import json
from asynctest import patch
from aiohttp.test_utils import make_mocked_request
from transaction.get_unsigned_transfer import get_unsigned_transfer_from_request, get_unsigned_transfer, get_signers, get_threshold_weight
from wallet.tests.factory.wallet import StellarWallet


@patch('transaction.get_unsigned_transfer.get_unsigned_transfer')
async def test_get_transaction_from_request(mock_get_unsigned_transfer):
    req = make_mocked_request('GET', '/wallet/{}/transaction/transfer?destination=GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6&amount=100'.format('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'),
        match_info={'account_address': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'}
    )
    await get_unsigned_transfer_from_request(req)
    assert mock_get_unsigned_transfer.call_count == 1


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
        "@transaction_url": "localhost:8081/transaction/4038c87310497828ed6243b9678c1ebd072e907a8cf18fb62a892e2680ed837e",
        "min_signer": 1,
        "signers": [
            {
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "weight": 1
            }
        ],
        "unsigned_xdr": "AAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAZAB3A5sAAAAFAAAAAAAAAAAAAAABAAAAAQAAAADOf93UUiwNNmwwYj2/XOv/KuhgA2mooc0ID+GYa49siQAAAAEAAAAA2ZlGnrw2xRHbxWDQCoRQRz8b/Ua+KYUBVdlcf4Ec5bEAAAABSFRLTgAAAAAUaMgWvAL6cM0x6BLXsGqY3oRp+AHRtOvJoG9V7u6tTgAAAAA7msoAAAAAAAAAAAA="
    }
    assert json.loads(result.text) == expect_data


@asyncio.coroutine
@patch('transaction.get_unsigned_transfer.get_wallet')
async def test_get_signers(mock_address):
    instance = mock_address.return_value
    balances = [
        {
            'balance': '9.9999200',
            'asset_type': 'native'
        }]
    mock_address.return_value = StellarWallet(balances)

    result = await get_signers('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI')
    expect_result = [{
            'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
            'weight': 1
        }, {
            'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
            'weight': 1
        }]
    assert result == expect_result


@asyncio.coroutine
@patch('transaction.get_unsigned_transfer.get_wallet')
async def test_get_threshold_weight_low_threshold(mock_address):
    instance = mock_address.return_value
    balances = [
        {
            'balance': '9.9999200',
            'asset_type': 'native'
        }]
    mock_address.return_value = StellarWallet(balances)

    result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'allow_trust')
    assert result == 1


@asyncio.coroutine
@patch('transaction.get_unsigned_transfer.get_wallet')
async def test_get_threshold_weight_med_threshold(mock_address):
    instance = mock_address.return_value
    balances = [
        {
            'balance': '9.9999200',
            'asset_type': 'native'
        }]
    mock_address.return_value = StellarWallet(balances)

    result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'payment')
    assert result == 2


@asyncio.coroutine
@patch('transaction.get_unsigned_transfer.get_wallet')
async def test_get_threshold_weight_high_threshold(mock_address):
    instance = mock_address.return_value
    balances = [
        {
            'balance': '9.9999200',
            'asset_type': 'native'
        }]
    mock_address.return_value = StellarWallet(balances)

    result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'set_signer')
    assert result == 2
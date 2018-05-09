import asyncio
import json

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request, unittest_run_loop
from asynctest import patch
from stellar_base.utils import AccountNotExistError
from tests.test_utils import BaseTestClass

from conf import settings
from transaction.get_unsigned_transfer import (get_signers,
                                               get_threshold_weight,
                                               get_unsigned_transfer,
                                               get_unsigned_transfer_from_request)
from wallet.tests.factory.wallet import StellarWallet


class TestGetUnsignedTransaction(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.get_unsigned_transfer.get_wallet')
    @patch('transaction.get_unsigned_transfer.get_unsigned_transfer')
    async def test_get_transaction_from_request(self, mock_get_unsigned_transfer, mock_address):
        mock_get_unsigned_transfer.return_value = {}
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        req = make_mocked_request('GET', f'/wallet/{source_address}/transaction/transfer?destination={destination_address}&amount=100',
            match_info={'wallet_address': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'}
        )
        resp = await get_unsigned_transfer_from_request(req)
        assert resp.status == 200
        mock_get_unsigned_transfer.assert_called_once_with(source_address, destination_address, '100')


    @unittest_run_loop
    @patch('transaction.get_unsigned_transfer.get_unsigned_transfer')
    async def test_get_transaction_from_request_invalid_query(self, mock_get_unsigned_transfer):
        req = make_mocked_request('GET', '/wallet/{}/transaction/transfer?des=GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6&amount=100'.format('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'),
            match_info={'wallet_address': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'}
        )

        with pytest.raises(KeyError) as context:
            await get_unsigned_transfer_from_request(req)
        assert str(context.value) == '"Key not found: \'destination\'"'


    @unittest_run_loop
    @patch('transaction.get_unsigned_transfer.get_wallet')
    @patch('transaction.get_unsigned_transfer.get_unsigned_transfer')
    async def test_get_transaction_from_request_account_does_not_exist(self, mock_get_unsigned_transfer, mock_address):
        req = make_mocked_request('GET', '/wallet/{}/transaction/transfer?destination=GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6&amount=100'.format('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'),
            match_info={'wallet_address': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'}
        )

        mock_address.side_effect = web.HTTPNotFound()

        with pytest.raises(web.HTTPNotFound) as context:
            await get_unsigned_transfer_from_request(req)
        assert str(context.value) == 'Not Found'


    @unittest_run_loop
    @patch('transaction.get_unsigned_transfer.get_signers')
    @patch('transaction.get_unsigned_transfer.get_threshold_weight')
    async def test_get_unsigned_transfer(self, mock_get_threshold_weight, mock_get_signer):
        mock_get_threshold_weight.return_value = 1
        mock_get_signer.return_value = [{
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "weight": 1
        }]

        result = await get_unsigned_transfer(
            'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
            'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6',
            '100')

        host = settings.get('HOST', None)
        expect_data = {
            "@id": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "@url": f'{host}/wallet/GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI/transaction/transfer',
            "@transaction_url": f'{host}/transaction/dc8616f8013dc8134fe1618f1b667b10e425fed18cd6f36e62b0bd8de1e726fe',
            "min_signer": 1,
            "signers": [
                {
                "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
                "weight": 1
                }
            ],
            "unsigned_xdr": "AAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAZAB3A5sAAAAGAAAAAAAAAAAAAAABAAAAAQAAAADOf93UUiwNNmwwYj2/XOv/KuhgA2mooc0ID+GYa49siQAAAAEAAAAA2ZlGnrw2xRHbxWDQCoRQRz8b/Ua+KYUBVdlcf4Ec5bEAAAABSFRLTgAAAADkHacjwpeFWz5txveZ4sJ3pEmTzpdS9fiBscDwpmoppgAAAAA7msoAAAAAAAAAAAA="
        }
        assert result == expect_data

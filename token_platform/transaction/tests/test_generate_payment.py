import asyncio
import json

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request, unittest_run_loop
from asynctest import patch
from stellar_base.utils import AccountNotExistError
from tests.test_utils import BaseTestClass

from conf import settings
from transaction.generate_payment import (get_signers,
                                               get_threshold_weight,
                                               generate_payment,
                                               generate_payment_from_request,
                                               build_unsigned_transfer)
from wallet.tests.factory.wallet import StellarWallet


class TestGetUnsignedTransaction(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet')
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request(self, mock_generate_payment, mock_address):
        mock_generate_payment.return_value = {}
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'

        data = {'target_address': destination_address, 'amount': 10}
        url = f'/wallet/{source_address}/generate-payment'
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 200
        mock_generate_payment.assert_called_once_with(source_address, destination_address, 10, None)


    @unittest_run_loop
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request_invalid_parameter(self, mock_generate_payment):
        mock_generate_payment.return_value = {}
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'

        data = {'target': destination_address, 'amount': 10}
        url = f'/wallet/{source_address}/generate-payment'
        resp = await self.client.request('POST', url, json=data)
        print(resp)
        assert resp.status == 400
        assert resp.reason == 'Bad Request'


    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet')
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request_account_does_not_exist(self, mock_generate_payment, mock_address):
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        data = {'target_address': destination_address, 'amount': 10}
        url = f'/wallet/{source_address}/generate-payment'

        mock_address.side_effect = web.HTTPNotFound()
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 404
        assert resp.reason == 'Not Found'


    @unittest_run_loop
    @patch('transaction.generate_payment.get_signers')
    @patch('transaction.generate_payment.get_threshold_weight')
    async def test_generate_payment(self, mock_get_threshold_weight, mock_get_signer):
        mock_get_threshold_weight.return_value = 1
        mock_get_signer.return_value = [{
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "weight": 1
        }]

        result = await generate_payment(
            'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
            'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6',
            '100', None)

        host = settings.get('HOST', None)
        expect_data = {
            "@id": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "@url": f'{host}/wallet/GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI/generate-payment',
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

    @unittest_run_loop
    async def test_build_unsigned_transfer_with_memo(self):

        result = build_unsigned_transfer('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 10, 1, 'memo')
        assert result == ('AAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAZAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAEAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAFIVEtOAAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAAAX14QAAAAAAAAAAAA==', '62bcef44d2d06a4657850849e94ada319fe398d5dd091907916876ded24b8167')

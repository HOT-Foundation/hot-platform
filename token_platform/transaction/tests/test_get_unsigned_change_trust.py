import asyncio
import json

from tests.test_utils import BaseTestClass

import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from conf import settings
from transaction.get_unsigned_change_trust import (get_signers,
                                                   get_threshold_weight,
                                                   get_unsigned_change_trust,
                                                   get_unsigned_change_trust_from_request,
                                                   build_unsigned_change_trust)
from wallet.tests.factory.wallet import StellarWallet
from router import reverse


class TestGetUnsignedChangeTrust(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.get_unsigned_change_trust.get_unsigned_change_trust')
    async def test_get_change_trust_from_request_success(self, mock_get_unsigned_change_trust):
        mock_get_unsigned_change_trust.return_value = {}
        wallet_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        transaction_source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        transaction_url = reverse('change-trust', wallet_address=wallet_address)
        params = 'transaction-source-address={}'.format(transaction_source_address)
        url = f'{transaction_url}?{params}'

        resp = await self.client.request('GET', url)
        assert resp.status == 200
        mock_get_unsigned_change_trust.assert_called_once_with(wallet_address, transaction_source_address)


    @unittest_run_loop
    @patch('transaction.get_unsigned_change_trust.get_signers')
    @patch('transaction.get_unsigned_change_trust.get_threshold_weight')
    async def test_get_unsigned_change_trust_success(self, mock_get_threshold_weight, mock_get_signer):
        mock_get_threshold_weight.return_value = 1
        mock_get_signer.return_value = [{
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "weight": 1
        }]

        result = await get_unsigned_change_trust(
            'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI')

        expect_data = {
            "@id": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "@url": f"{settings['HOST']}{reverse('change-trust', wallet_address='GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI')}",
            "@transaction_url": f"{settings['HOST']}{reverse('transaction', transaction_hash='ae7d705bf2655f0581d3f7f8bfbbc567f9fee5e9d4632bfb0adb2c74194fbed2')}",
            "min_signer": 1,
            "signers": [
                {
                "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
                "weight": 1
                }
            ],
            "xdr": "AAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAZAB3A5sAAAAGAAAAAAAAAAAAAAABAAAAAQAAAADOf93UUiwNNmwwYj2/XOv/KuhgA2mooc0ID+GYa49siQAAAAYAAAABSFRLTgAAAADkHacjwpeFWz5txveZ4sJ3pEmTzpdS9fiBscDwpmoppgFjRXhdigAAAAAAAAAAAAA=",
            "transaction_hash": "ae7d705bf2655f0581d3f7f8bfbbc567f9fee5e9d4632bfb0adb2c74194fbed2"
        }

        assert result == expect_data

    @unittest_run_loop
    @patch('transaction.get_unsigned_change_trust.Builder')
    async def test_build_change_trust_transaction_with_wrong_parameter(self, mock_builder):
        instance = mock_builder.return_value
        instance.append_trust_op.return_value = {}

        instance.gen_xdr = Exception('cannot find sequence')

        with pytest.raises(web.HTTPNotFound):
            build_unsigned_change_trust('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI')

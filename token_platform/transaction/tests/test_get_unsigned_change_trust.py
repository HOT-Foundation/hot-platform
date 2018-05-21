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


class TestGetUnsignedChangeTrust(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.get_unsigned_change_trust.get_unsigned_change_trust')
    async def test_get_change_trust_from_request_success(self, mock_get_unsigned_change_trust):
        mock_get_unsigned_change_trust.return_value = {}
        wallet_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        resp = await self.client.request('GET', '/wallet/{}/transaction/change-trust'.format(wallet_address))
        assert resp.status == 200
        mock_get_unsigned_change_trust.assert_called_once_with(wallet_address)


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
            'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI')

        expect_data = {
            "@id": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "@url": f"{settings['HOST']}/wallet/GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI/transaction/change-trust",
            "@transaction_url": f"{settings['HOST']}/transaction/bbf17ffd2de5a1fafd1644b506ad601402426fe0633a168edec05522d30cf09c",
            "min_signer": 1,
            "signers": [
                {
                "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
                "weight": 1
                }
            ],
            "unsigned_xdr": "AAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAZAB3A5sAAAAGAAAAAAAAAAAAAAABAAAAAQAAAADOf93UUiwNNmwwYj2/XOv/KuhgA2mooc0ID+GYa49siQAAAAYAAAABSFRLTgAAAADkHacjwpeFWz5txveZ4sJ3pEmTzpdS9fiBscDwpmoppn//////////AAAAAAAAAAA=",
            "transaction_hash": "bbf17ffd2de5a1fafd1644b506ad601402426fe0633a168edec05522d30cf09c"
        }

        assert result == expect_data

    @unittest_run_loop
    @patch('transaction.get_unsigned_change_trust.Builder')
    async def test_build_change_trust_transaction_with_wrong_parameter(self, mock_builder):
        instance = mock_builder.return_value
        instance.append_trust_op.return_value = {}

        instance.gen_xdr = Exception('cannot find sequence')

        with pytest.raises(web.HTTPNotFound):
            build_unsigned_change_trust('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI')

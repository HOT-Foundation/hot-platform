from tests.test_utils import BaseTestClass

from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from conf import settings
from escrow.generate_pre_signed_tx_xdr import (get_current_sequence_number,
                                               get_presigned_tx_xdr,
                                               get_presigned_tx_xdr_from_request,
                                               get_signers,
                                               get_threshold_weight)


class TestGeneratePreSignedTxXDR(BaseTestClass):
    @unittest_run_loop
    @patch('escrow.generate_pre_signed_tx_xdr.get_presigned_tx_xdr')
    async def test_get_presigned_tx_xdr_from_request(self, mock_get_transaction):
        json_request = {
            "stellar_escrow_address": 'GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY',
            "stellar_merchant_address": 'GDR3AGPEISYHLHAB6EVP3HD4COCIT7SPGL7WTSIZR3PNBWKFKZGTUJSNr',
            "stellar_hotnow_address": 'GABEAFZ7POCHDY4YCQMRAGVVXEEO4XWYKBY4LMHHJRHTC4MZQBWS6NL6',
            "starting_balance": 10,
            "expriring_date": '2018-05-02',
            "cost_per_tx": 5
        }

        mock_get_transaction.return_value = {}
        resp = await self.client.request("POST", "/presigned-transfer", json=json_request)
        assert resp.status == 200
        # mock_get_transaction.assert_called_once()
    

    @unittest_run_loop
    @patch('escrow.generate_pre_signed_tx_xdr.get_threshold_weight')
    @patch('escrow.generate_pre_signed_tx_xdr.get_signers')
    @patch('escrow.generate_pre_signed_tx_xdr.get_current_sequence_number')
    @patch('escrow.generate_pre_signed_tx_xdr.build_unsigned_transfer')
    async def test_get_presigned_tx_xdr(self, mock_biulder, mock_sequence, mock_signer, mock_threshold):
        mock_biulder.return_value = ('xdr', 'hash')
        mock_sequence.return_value = '1'
        mock_signer.return_value = []
        mock_threshold.return_value = 2
        result = await get_presigned_tx_xdr(
            'GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY',
            'GDR3AGPEISYHLHAB6EVP3HD4COCIT7SPGL7WTSIZR3PNBWKFKZGTUJSNr',
            'GABEAFZ7POCHDY4YCQMRAGVVXEEO4XWYKBY4LMHHJRHTC4MZQBWS6NL6',
            10,
            '2018-05-02',
            5
        )

        expect = {
            "min_signer": 2,
            "signers": [],
            "xdr": [
                {
                "@id": "GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY",
                "@url": "http://hotnow-token-platform:8081/wallet/GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY/transaction/transfer",
                "@transaction_url": "http://hotnow-token-platform:8081/transaction/hash",
                "unsigned_xdr": "xdr"
                },
                {
                "@id": "GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY",
                "@url": "http://hotnow-token-platform:8081/wallet/GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY/transaction/transfer",
                "@transaction_url": "http://hotnow-token-platform:8081/transaction/hash",
                "unsigned_xdr": "xdr"
                }
            ]
        }

        assert result == expect

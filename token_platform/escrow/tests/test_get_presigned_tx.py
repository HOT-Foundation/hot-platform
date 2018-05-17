from decimal import Decimal

from tests.test_utils import BaseTestClass

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request, unittest_run_loop
from asynctest import patch
from conf import settings
from escrow.generate_pre_signed_tx_xdr import (get_current_sequence_number,
                                               get_presigned_tx_xdr,
                                               get_presigned_tx_xdr_from_request,
                                               get_signers,
                                               get_threshold_weight)


class TestGeneratePreSignedTxXDR(BaseTestClass):
    @unittest_run_loop
    @patch('escrow.generate_pre_signed_tx_xdr.get_escrow_wallet_detail')
    @patch('escrow.generate_pre_signed_tx_xdr.get_presigned_tx_xdr')
    async def test_get_presigned_tx_xdr_from_request(self, mock_get_transaction, mock_get_wallet):
        escrow_address = "GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY"
        mock_get_transaction.return_value = {}
        host = settings.get('HOST', None)
        mock_get_wallet.return_value = {
            '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
            '@url': f'{host}/escrow/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
            'asset': {
                'HTKN': '10.0000000',
                'XLM': '9.9999200'
            },
            'generate-wallet': f'{host}/escrow/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD/generate-wallet',
            'data': {
                'destination_address': 'GABEAFZ7POCHDY4YCQMRAGVVXEEO4XWYKBY4LMHHJRHTC4MZQBWS6NL6',
                'cost_per_transaction': '5'
            }
        }

        resp = await self.client.request("POST", "/escrow/{}/generate-presigned-transections".format(escrow_address), json={})
        assert resp.status == 200

        mock_get_wallet.assert_called_once_with(
            escrow_address
        )

        destination_address = "GABEAFZ7POCHDY4YCQMRAGVVXEEO4XWYKBY4LMHHJRHTC4MZQBWS6NL6"
        balance = Decimal("10.0000000")
        cost_per_tx = Decimal("5")

        mock_get_transaction.assert_called_once_with(
            escrow_address,
            destination_address,
            balance,
            cost_per_tx
        )

    @unittest_run_loop
    @patch('escrow.generate_pre_signed_tx_xdr.get_escrow_wallet_detail')
    @patch('escrow.generate_pre_signed_tx_xdr.get_presigned_tx_xdr')
    async def test_get_presigned_tx_xdr_cannot_get_value_in_data(self, mock_get_transaction, mock_get_wallet):
        host = settings.get('HOST', None)
        escrow_address = "GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY"
        mock_get_transaction.return_value = {}
        mock_get_wallet.return_value = {
            '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
            '@url': f'{host}/escrow/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
            'asset': {
                'HTKN': '10.0000000',
                'XLM': '9.9999200'
            },
            'generate-wallet': f'{host}/escrow/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD/generate-wallet',
            'data': {
                'source': 'GABEAFZ7POCHDY4YCQMRAGVVXEEO4XWYKBY4LMHHJRHTC4MZQBWS6NL6'
            }
        }

        req = make_mocked_request("POST", "/escrow/{}/generate-presigned-transections".format(escrow_address),
            match_info={'wallet_address': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'}
        )

        with pytest.raises(KeyError) as context:
            await get_presigned_tx_xdr_from_request(req)
        assert str(context.value) ==  "'destination_address'"


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
            'GABEAFZ7POCHDY4YCQMRAGVVXEEO4XWYKBY4LMHHJRHTC4MZQBWS6NL6',
            Decimal('10.0000000'),
            Decimal('5')
        )

        expect = {
            "min_signer": 2,
            "signers": [],
            "xdr": [
                {
                "@id": "GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY",
                "@url": "/wallet/GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY/transaction/transfer",
                "@transaction_url": "/transaction/hash",
                "xdr": "xdr",
                "sequence_number": 2,
                "transaction_hash": "hash"
                },
                {
                "@id": "GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY",
                "@url": "/wallet/GAH6333FKTNQGSFSDLCANJIE52N7IGMS7DUIWR6JIMQZE7XKWEQLJQAY/transaction/transfer",
                "@transaction_url": "/transaction/hash",
                "xdr": "xdr",
                "sequence_number": 3,
                "transaction_hash": "hash"
                }
            ]
        }
        assert result == expect

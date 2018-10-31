import pytest
from aiohttp.test_utils import unittest_run_loop
from aiohttp.web_exceptions import HTTPBadRequest, HTTPInternalServerError, HTTPNotFound
from aioresponses import aioresponses
from asynctest import patch
from stellar_base.builder import Builder
from stellar_base.keypair import Keypair
from tests.test_utils import BaseTestClass

from conf import settings
from transaction.transaction import (
    get_current_sequence_number,
    get_reason_transaction,
    get_signers,
    get_threshold_weight,
    get_transaction_by_memo,
    get_transaction_hash,
    is_duplicate_transaction,
    submit_transaction,
)
from wallet.tests.factory.wallet import StellarWallet
from stellar.wallet import Wallet


class TestSubmitTransaction(BaseTestClass):
    class WrongResponseBadRequest:
        def __init__(self):
            self.status = 400

        async def json(self):
            return {'status': 400}

    class WrongResponseNotFound:
        def __init__(self):
            self.status = 404

        async def json(self):
            return {'status': 404}

    class SuccessResponse:
        def __init__(self):
            self.status = 200

        async def json(self):
            return {'status': 200}

    @unittest_run_loop
    @patch('transaction.transaction.aiohttp.ClientSession.post')
    async def test_submit_transaction_success(self, mock_post) -> None:
        session = mock_post.return_value
        session.__aenter__.return_value = self.SuccessResponse()
        signed_xdr = 'Testtest'
        result = await submit_transaction(signed_xdr)
        expect = self.SuccessResponse()
        assert result == await expect.json()

    @unittest_run_loop
    @patch('transaction.transaction.aiohttp.ClientSession.post')
    async def test_submit_transaction_fail_not_found(self, mock_post) -> None:
        session = mock_post.return_value
        session.__aenter__.return_value = self.WrongResponseBadRequest()
        with pytest.raises(HTTPBadRequest):
            signed_xdr = 'Testtest'
            result = await submit_transaction(signed_xdr)

    @unittest_run_loop
    @patch('transaction.transaction.aiohttp.ClientSession.post')
    async def test_submit_transaction_fail_bad_request(self, mock_post) -> None:
        session = mock_post.return_value
        session.__aenter__.return_value = self.WrongResponseNotFound()
        with pytest.raises(HTTPNotFound):
            signed_xdr = 'Testtest'
            result = await submit_transaction(signed_xdr)


class TestDuplicateTransaction(BaseTestClass):
    class SuccessResponse:
        def __init__(self):
            self.status = 200

        async def json(self):
            return {"id": 'testteestsetbbdf'}

    class WrongResponse:
        def __init__(self):
            self.status = 400

        async def json(self):
            return {
                "title": "Resource Missing",
                "status": 404,
                "detail": "The resource at the url requested was not found.  This is usually occurs for one of two reasons:  The url requested is not valid, or no data in our database could be found with the parameters provided.",
            }

    @unittest_run_loop
    @patch('transaction.transaction.aiohttp.ClientSession.get')
    async def test_is_duplicate_transaction_duplicate_when_id_exist(self, mock_get) -> None:
        session = mock_get.return_value
        session.__aenter__.return_value = self.SuccessResponse()

        tx_hash = 'e11b7a3677fdd45c885e8fb49d0079d083ee8a5cab08e32b00126172abb05111'
        result = await is_duplicate_transaction(tx_hash)
        assert result == True

    @unittest_run_loop
    @patch('transaction.transaction.aiohttp.ClientSession.get')
    async def test_is_duplicate_transaction_not_duplicate_when_get_not_found(self, mock_get) -> None:
        session = mock_get.return_value
        session.__aenter__.return_value = self.WrongResponse()

        tx_hash = 'e11b7a3677fdd45c885'
        result = await is_duplicate_transaction(tx_hash)
        assert result == False


class TestGetTransactionHash(BaseTestClass):
    async def setUpAsync(self):
        self.address = 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF'
        self.tx_hash = '4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9'
        self.memo = '1'
        self.result = {'transaction_hash': 'test'}

    @unittest_run_loop
    @patch('transaction.transaction.get_transaction_by_memo')
    async def test_get_transaction_hash_success(self, mock_transaction_by_memo):
        mock_transaction_by_memo.return_value = self.result

        result = await get_transaction_hash(self.address, self.memo)
        assert result == self.result['transaction_hash']

    @unittest_run_loop
    @patch('transaction.transaction.get_transaction_by_memo')
    async def test_get_transaction_hash_fail(self, mock_transaction_by_memo):
        mock_transaction_by_memo.return_value = False

        result = await get_transaction_hash(self.address, self.memo)
        assert not result


class TestGetcurrentSequenceNumber(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.transaction.stellar.wallet.get_stellar_wallet')
    async def test_get_sequence_number_success(self, mock_wallet) -> None:
        instance = mock_wallet.return_value
        instance.sequence = '5'

        wallet_address = 'GASF2Q2GZMQMMNSYDU34MU4GJKSZPSN7FYKQEMNH4QJMVE3JR3C3I3N5'
        result = await get_current_sequence_number(wallet_address)
        assert isinstance(result, str)
        assert result == '5'


class TestGetSigner(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_signers(self, mock_address):

        signers = [
            {
                'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'weight': 1,
                'key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'type': 'ed25519_public_key',
            },
            {
                'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'weight': 1,
                'key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'type': 'ed25519_public_key',
            },
            {
                'public_key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
                'weight': 0,
                'key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
                'type': 'ed25519_public_key',
            },
        ]

        mock_address.return_value = Wallet('test-address', 'test-balance', 'test-sequence', {}, signers, {}, {})

        result = await get_signers('test-address')
        expect_result = [
            {'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF', 'weight': 1},
            {'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'weight': 1},
        ]

        assert result == expect_result


class TestGetThreshold(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_threshold_weight_low_threshold(self, mock_address):
        balances = [{'balance': '9.9999200', 'asset_type': 'native'}]
        mock_address.return_value = StellarWallet(balances)

        result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'allow_trust')
        assert result == 1

    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_threshold_weight_med_threshold(self, mock_address):
        balances = [{'balance': '9.9999200', 'asset_type': 'native'}]
        mock_address.return_value = StellarWallet(balances)

        result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'payment')
        assert result == 2

    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_threshold_weight_high_threshold(self, mock_address):
        balances = [{'balance': '9.9999200', 'asset_type': 'native'}]
        mock_address.return_value = StellarWallet(balances)

        result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'set_signer')
        assert result == 2

    @unittest_run_loop
    @patch('transaction.transaction.stellar.wallet.get_transaction_by_wallet')
    async def test_get_transaction_by_memo_success(self, mock_get_transaction):
        mock_get_transaction.return_value = [{"memo_type": "text", "memo": "testmemo", "hash": "testhash"}]

        result = await get_transaction_by_memo('GD3PPDLKXRDM57UV7QDFIHLLRCLM4KGVIA43GEM7ZOT7EHK5TR3Z5G6I', 'testmemo')
        assert 'error' in result.keys()
        assert 'url' in result.keys()

    @unittest_run_loop
    @patch('transaction.transaction.stellar.wallet.get_transaction_by_wallet')
    async def test_get_transaction_by_memo_not_found(self, mock_get_transaction):
        mock_get_transaction.return_value = []

        result = await get_transaction_by_memo('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'testmemo')
        assert not result


class TestGetReasonTransaction(BaseTestClass):
    @unittest_run_loop
    async def test_get_reason_transacton_successfully(self):
        respons_data = {
            "extras": {"result_codes": {"transaction": "tx_failed", "operations": ["op_no_destination", "op_success"]}}
        }
        resp = get_reason_transaction(respons_data)
        self.assertEqual(resp, 'op_no_destination/op_success')

    @unittest_run_loop
    async def test_get_reason_transacton_not_found_value(self):
        respons_data = {"extras": {"result_codes": {"transaction": "tx_bad_seq"}}}
        resp = get_reason_transaction(respons_data)
        self.assertEqual(resp, None)

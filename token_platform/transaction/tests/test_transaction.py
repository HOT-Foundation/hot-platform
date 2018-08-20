import pytest
from aiohttp.test_utils import unittest_run_loop
from aiohttp.web_exceptions import HTTPBadRequest, HTTPInternalServerError
from asynctest import patch
from stellar_base.builder import Builder
from stellar_base.keypair import Keypair
from tests.test_utils import BaseTestClass

from conf import settings
from transaction.tests.factory.horizon import HorizonData
from transaction.transaction import (get_current_sequence_number,
                                     get_reason_transaction, get_signers,
                                     get_threshold_weight,
                                     get_transaction_by_memo,
                                     get_transaction_hash,
                                     is_duplicate_transaction,
                                     submit_transaction)
from wallet.tests.factory.wallet import StellarWallet


class TestSubmitTransaction(BaseTestClass):

    class WrongResponse():
        def submit(self, tx_hash):
            raise ValueError('response is not json format.')

    class SuccessResponse():
        def __init__(self):
            self.status = 200

        async def json(self):
            return { 'status': 200 }

    @unittest_run_loop
    @patch('aiohttp.ClientSession.post')
    async def test_submit_transaction_success(self, mock_client) -> None:
        session = mock_client.return_value
        session.__aenter__.return_value = self.SuccessResponse()
        signed_xdr = 'Testtest'
        result = await submit_transaction(signed_xdr)
        expect = self.SuccessResponse()
        assert result == await expect.json()

    @unittest_run_loop
    async def test_submit_transaction_fail_with_duplicate_xdr(self) -> None:
        with pytest.raises(HTTPBadRequest):
            signed_xdr = b'AAAAACRdQ0bLIMY2WB03xlOGSqWXyb8uFQIxp+QSypNpjsW0AAAAZAB79gEAAAAHAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAbUsVq2bqEoCf7vIHxSuFBHDqxrZiYvtyqyavFkpA9wQAAAABDzN9gAAAAAAAAAABaY7FtAAAAEB0OSEaK6FTDW3imY9vU/jFe3dDhz0j5/656Kpns/uzBdSMUvl9q8ZNQes7ASTp98hgsxfZBlVnYAr0jzwY05MI'
            result = await submit_transaction(signed_xdr)

    @unittest_run_loop
    async def test_submit_transaction_fail_with_wrong_xdr_value(self) -> None:
        with pytest.raises(HTTPBadRequest):
            signed_xdr = b'AAAAACRdQ0bLIMY2WB03xlOGSqWXy'
            result = await submit_transaction(signed_xdr)

    @unittest_run_loop
    @patch('transaction.transaction.Horizon')
    async def test_submit_transaction_fail_with_wrong_response_format(self, mock_horizon) -> None:
        mock_horizon.return_value = self.WrongResponse()
        with pytest.raises(HTTPBadRequest):
            signed_xdr = 'Testtest'
            result = await submit_transaction(signed_xdr)


class TestDuplicateTransaction(BaseTestClass):

    @unittest_run_loop
    @patch('transaction.transaction.Horizon')
    async def test_is_duplicate_transaction_duplicate_when_id_exist(self, mock_horizon) -> None:
        instance = mock_horizon.return_value
        instance.transaction.return_value = {"id": 'testteestsetbbdf'}

        tx_hash = 'e11b7a3677fdd45c885e8fb49d0079d083ee8a5cab08e32b00126172abb05111'
        result = await is_duplicate_transaction(tx_hash)
        assert result == True

    @unittest_run_loop
    @patch('transaction.transaction.Horizon')
    async def test_is_duplicate_transaction_not_duplicate_when_get_not_found(self, mock_horizon) -> None:
        instance = mock_horizon.return_value
        instance.transaction.return_value = {
                "title": "Resource Missing",
                "status": 404,
                "detail": "The resource at the url requested was not found.  This is usually occurs for one of two reasons:  The url requested is not valid, or no data in our database could be found with the parameters provided."
        }

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

    class Account():
        def get(self, str):
            return '1234566789'

    @unittest_run_loop
    @patch('transaction.transaction.Horizon')
    async def test_get_sequence_number_success(self, mock_horizon) -> None:
        instance = mock_horizon.return_value
        instance.account.return_value = self.Account()

        wallet_address = 'GASF2Q2GZMQMMNSYDU34MU4GJKSZPSN7FYKQEMNH4QJMVE3JR3C3I3N5'
        result = await get_current_sequence_number(wallet_address)
        assert isinstance(result, str)
        assert result == '1234566789'


class TestGetSigner(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_signers(self, mock_address):
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


class TestGetThreshold(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_threshold_weight_low_threshold(self, mock_address):
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)

        result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'allow_trust')
        assert result == 1

    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_threshold_weight_med_threshold(self, mock_address):
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)

        result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'payment')
        assert result == 2

    @unittest_run_loop
    @patch('transaction.transaction.get_wallet')
    async def test_get_threshold_weight_high_threshold(self, mock_address):
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)

        result = await get_threshold_weight('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'set_signer')
        assert result == 2

    @unittest_run_loop
    async def test_get_transaction_by_memo_success(self):
        result = await get_transaction_by_memo('GD3PPDLKXRDM57UV7QDFIHLLRCLM4KGVIA43GEM7ZOT7EHK5TR3Z5G6I', 'testmemo')
        assert 'error' in result.keys()
        assert 'url' in result.keys()

    @unittest_run_loop
    async def test_get_transaction_by_memo_not_found(self):
        result = await get_transaction_by_memo('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'testmemo')
        assert not result


class TestGetReasonTransaction(BaseTestClass):
    @unittest_run_loop
    async def test_get_reason_transacton_successfully(self):
        respons_data = {
            "extras": {
                "result_codes": {
                    "transaction": "tx_failed",
                    "operations": [
                        "op_no_destination",
                        "op_success"
                    ]
                }
            }
        }
        resp = get_reason_transaction(respons_data)
        self.assertEqual(resp, 'op_no_destination/op_success')

    @unittest_run_loop
    async def test_get_reason_transacton_not_found_value(self):
        respons_data = {
            "extras": {
                "result_codes": {
                    "transaction": "tx_bad_seq"
                }
            }
        }
        resp = get_reason_transaction(respons_data)
        self.assertEqual(resp, None)

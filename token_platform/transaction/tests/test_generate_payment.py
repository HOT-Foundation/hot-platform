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
from transaction.transaction import get_transaction_by_memo
from wallet.tests.factory.wallet import StellarWallet
from router import reverse


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

        data = {'target_address': destination_address, 'amount_xlm': 10, 'amount_htkn': 5}
        url = reverse('generate-payment', wallet_address=source_address)
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 200
        mock_generate_payment.assert_called_once_with(source_address, destination_address, 5, 10, None, None)

    @unittest_run_loop
    @patch('transaction.generate_payment.get_transaction_by_memo')
    @patch('transaction.generate_payment.get_wallet')
    async def test_get_transaction_from_request_already_submitted(self, mock_address, mock_transaction_by_memo):

        mock_transaction_by_memo.return_value = {
            'message' : 'Transaction is already submited',
            'url' : reverse('transaction', transaction_hash='0b309e40e40809e34e7765062e8ff393dd4e542d05f59a22719655e84c557257')
        }

        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GBFAIH5WKAJQ77NG6BZG7TGVGXHPX4SQLIJ7BENJMCVCZSUZPSISCLU5'
        meta = 'testmemo'

        data = {'target_address': destination_address, 'amount_xlm': 10, 'amount_htkn': 5, 'meta': meta}
        url = reverse('generate-payment', wallet_address=source_address)
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        text = await resp.json()
        assert text == mock_transaction_by_memo.return_value
        mock_transaction_by_memo.assert_called_once_with(source_address, meta)


    @unittest_run_loop
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request_invalid_parameter(self, mock_generate_payment):
        mock_generate_payment.return_value = {}
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'

        data = {'target': destination_address, 'amount': 10}
        url = reverse('generate-payment', wallet_address=source_address)
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
        data = {'target_address': destination_address, 'amount_htkn': 10}
        url = reverse('generate-payment', wallet_address=source_address)

        mock_address.side_effect = web.HTTPNotFound()
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 404
        assert resp.reason == 'Not Found'


    @unittest_run_loop
    @patch('transaction.generate_payment.build_unsigned_transfer')
    @patch('transaction.generate_payment.get_signers')
    @patch('transaction.generate_payment.get_threshold_weight')
    async def test_generate_payment(self, mock_get_threshold_weight, mock_get_signer, mock_build):
        mock_get_threshold_weight.return_value = 1
        mock_get_signer.return_value = [{
            "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "weight": 1
        }]
        mock_build.return_value = ('xdr', 'tx_hash')

        result = await generate_payment(
            'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
            'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6',
            '100', '0', None, None)

        expect_data = {
            "@id": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
            "@url": reverse('generate-payment', wallet_address='GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'),
            "@transaction_url": reverse('transaction', transaction_hash='tx_hash'),
            "min_signer": 1,
            "signers": [
                {
                "public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
                "weight": 1
                }
            ],
            "xdr": "xdr",
            "transaction_hash": "tx_hash"
        }
        assert result == expect_data

    @unittest_run_loop
    @patch('transaction.generate_payment.StellarAddress')
    async def test_build_unsigned_transfer_with_memo(self, mock_stellar):
        result = await build_unsigned_transfer('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 10, 0, 1, 'memo')
        assert result == ('AAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAZAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAEAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAFIVEtOAAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAAAX14QAAAAAAAAAAAA==', '62bcef44d2d06a4657850849e94ada319fe398d5dd091907916876ded24b8167')

    @unittest_run_loop
    @patch('transaction.generate_payment.StellarAddress')
    async def test_build_unsigned_transfer_with_xlm_amount(self, mock_stellar):
        result = await build_unsigned_transfer('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 0, 10, 1, 'memo')
        assert result == (
            'AAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAZAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAEAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAAAAAAABfXhAAAAAAAAAAAA',
            'c363b479e6dd1fb149c28251d71315d78144bb44e3daf0617eb07be554b8b59c'
        )

    @unittest_run_loop
    @patch('transaction.generate_payment.Builder')
    @patch('transaction.generate_payment.StellarAddress')
    async def test_build_unsigned_transfer_with_target_not_created(self, mock_stellar, mock_builder):
        class MockAddress(object):
            def get(self):
                raise AccountNotExistError('Resource Missing')

        mock_stellar.return_value = MockAddress()

        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_payment_op.return_value = 'test'
        instance.gen_xdr.return_value = b'unsigned-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'

        result = await build_unsigned_transfer('GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 0, 10, 1, 'memo')
        assert result == ('unsigned-xdr', '74782d68617368')

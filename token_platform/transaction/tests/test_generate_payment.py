import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from tests.test_utils import BaseTestClass

from conf import settings
from transaction.generate_payment import (get_signers,
                                               get_threshold_weight,
                                               generate_payment,
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
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'

        data = {'target_address': destination_address, 'transaction_source_address': transaction_source_address, 'amount_xlm': 10, 'amount_htkn': 5}
        url = reverse('generate-payment', wallet_address=source_address)
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 200
        mock_generate_payment.assert_called_once_with(transaction_source_address, source_address, destination_address, 5, 10, None, None)

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet')
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request_with_invalid_target(self, mock_generate_payment, mock_address):
        mock_generate_payment.return_value = {}
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'

        data = {'target_address': 'invalid', 'transaction_source_address': transaction_source_address, 'amount_xlm': 10, 'amount_htkn': 5}
        url = reverse('generate-payment', wallet_address=source_address)
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        mock_generate_payment.assert_not_called()

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet')
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request_with_invalid_memo_on(self, mock_generate_payment, mock_address):
        mock_generate_payment.return_value = {}
        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'

        data = {'target_address': 'invalid', 'transaction_source_address': transaction_source_address, 'amount_xlm': 10, 'amount_htkn': 5, 'memo_on': 'a'}
        url = reverse('generate-payment', wallet_address=source_address)
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        mock_generate_payment.assert_not_called()

    @unittest_run_loop
    @patch('transaction.generate_payment.get_transaction_by_memo')
    @patch('transaction.generate_payment.get_wallet')
    async def test_get_transaction_from_request_already_submitted(self, mock_address, mock_transaction_by_memo):

        mock_transaction_by_memo.return_value = {
            'error': 'Transaction is already submited',
            'url': '/transaction/db2c17818a6eeaae5f7e7a0a858fb62db4835509aa6d932c3fdd298e6e97d787',
            'transaction_hash': 'db2c17818a6eeaae5f7e7a0a858fb62db4835509aa6d932c3fdd298e6e97d787'
        }

        balances = [
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }
        ]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        destination_address = 'GBFAIH5WKAJQ77NG6BZG7TGVGXHPX4SQLIJ7BENJMCVCZSUZPSISCLU5'
        memo = 'testmemo'

        data = {'target_address': destination_address, 'transaction_source_address': transaction_source_address, 'amount_xlm': 10, 'amount_htkn': 5, 'memo': memo}
        url = reverse('generate-payment', wallet_address=source_address)
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        text = await resp.json()
        assert text == mock_transaction_by_memo.return_value
        mock_transaction_by_memo.assert_called_once_with(source_address, memo)

    @unittest_run_loop
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request_invalid_parameter(self, mock_generate_payment):
        mock_generate_payment.return_value = {}
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'

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
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'

        data = {'target_address': destination_address, 'transaction_source_address': transaction_source_address, 'amount_htkn': 10}
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
            'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
            'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
            'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6',
            '100', '0', None, None)

        expect_data = {
            "@id": reverse('generate-payment', wallet_address='GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'),
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
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_memo(self, mock_wallet):
        mock_wallet.return_value = {'asset': {settings['ASSET_CODE']: 10}}
        result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 10, 0, 1, 'memo')

        assert result == (
            'AAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAZAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAEAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAFIVEtOAAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAAAX14QAAAAAAAAAAAA==', 
            'b8722f7aab5b3dd1ef7718231b7e0a136881d008b90224fd1027823201d3be20'
        )

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_xlm_amount(self, mock_wallet):
        mock_wallet.return_value = {'asset': {}}
        result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 0, 10, 1, 'memo')

        assert result == (
            'AAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAZAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAEAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAAAAAAABfXhAAAAAAAAAAAA', 
            '9ede4ea6342ee85dd338e438c04c7539a0a8b3bc05b4bc6e3e474843e0c351d9'
        )

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_xlm_and_htkn_amount_with_trust(self, mock_wallet):
        mock_wallet.return_value = {'asset': {settings['ASSET_CODE']: 10}}
        result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 10, 10, 1, 'memo')
        
        assert result == (
            'AAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAyAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAIAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAAAAAAABfXhAAAAAAEAAAAAzn/d1FIsDTZsMGI9v1zr/yroYANpqKHNCA/hmGuPbIkAAAABAAAAANmZRp68NsUR28Vg0AqEUEc/G/1GvimFAVXZXH+BHOWxAAAAAUhUS04AAAAA5B2nI8KXhVs+bcb3meLCd6RJk86XUvX4gbHA8KZqKaYAAAAABfXhAAAAAAAAAAAA', 
            '79a187dda755f48669b6b5a924d6e7c287aa491ab917d177c63937b18a2b3afd'
        )

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_invalid_htkn(self, mock_wallet):
        mock_wallet.return_value = {'asset': {}}
        with pytest.raises(web.HTTPBadRequest) as context:
            result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 10, 10, 1, 'memo')

    @unittest_run_loop
    # @patch('transaction.generate_payment.StellarAddress')
    async def test_build_unsigned_transfer_with_target_not_created(self):

        # mock_stellar.side_effect = web.HTTPNotFound()

        with pytest.raises(web.HTTPNotFound):
            result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 0, 10, 1, 'memo')

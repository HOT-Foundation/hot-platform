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
        mock_generate_payment.assert_called_once_with(transaction_source_address, source_address, destination_address, 5, 10, None, None, None)

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
        body = await resp.json()
        assert body['message'] == 'Transaction is already submitted'
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
            '100', '0', None, None, None)

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
        result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 10, 0, 0, 1, 'memo')
        assert result == (
            'AAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAZAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAEAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAFIT1QAAAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAAAX14QAAAAAAAAAAAA==',
            '3e2d70f71460e522477cb78a5eea5c5a2a88e8ce030cccbc1dde3e39195639fa'
        )

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_xlm_amount(self, mock_wallet):
        mock_wallet.return_value = {'asset': {}}
        result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 0, 10, 0, 1, 'memo')

        assert result == (
            'AAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAZAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAEAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAAAAAAABfXhAAAAAAAAAAAA',
            '7cb70707e6532899c033068d07f9479a5d6e9fda37e47bafdcc70ddd9fc88dcc'
        )

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_xlm_and_htkn_amount_with_trust(self, mock_wallet):
        mock_wallet.return_value = {'asset': {settings['ASSET_CODE']: 10}}
        result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 10, 10, 0, 1, 'memo')
        assert result == (
            'AAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAAAyAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAIAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAAAAAAABfXhAAAAAAEAAAAAzn/d1FIsDTZsMGI9v1zr/yroYANpqKHNCA/hmGuPbIkAAAABAAAAANmZRp68NsUR28Vg0AqEUEc/G/1GvimFAVXZXH+BHOWxAAAAAUhPVAAAAAAA5B2nI8KXhVs+bcb3meLCd6RJk86XUvX4gbHA8KZqKaYAAAAABfXhAAAAAAAAAAAA',
            '8c68e2e653792304c554bb7db94989de6e08c7f74e70b5a2b4e2aa0716128dbf'
        )

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_usigned_transfer_with_tax_amount(self, mock_wallet):
        mock_wallet.return_value = {'asset': {settings['ASSET_CODE']: 10}}
        result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 10, 10, 2, 1, 'memo')
        assert result == (
            'AAAAAOQdpyPCl4VbPm3G95niwnekSZPOl1L1+IGxwPCmaimmAAABLAAAAAAAAAACAAAAAAAAAAEAAAAEbWVtbwAAAAMAAAABAAAAAM5/3dRSLA02bDBiPb9c6/8q6GADaaihzQgP4Zhrj2yJAAAAAQAAAADZmUaevDbFEdvFYNAKhFBHPxv9Rr4phQFV2Vx/gRzlsQAAAAAAAAAABfXhAAAAAAEAAAAAzn/d1FIsDTZsMGI9v1zr/yroYANpqKHNCA/hmGuPbIkAAAABAAAAANmZRp68NsUR28Vg0AqEUEc/G/1GvimFAVXZXH+BHOWxAAAAAUhPVAAAAAAA5B2nI8KXhVs+bcb3meLCd6RJk86XUvX4gbHA8KZqKaYAAAAABfXhAAAAAAEAAAAAzn/d1FIsDTZsMGI9v1zr/yroYANpqKHNCA/hmGuPbIkAAAABAAAAALA9mZ8grz8iu8VgoDleCsmyQofm9hN8oEMEYHzHbbbnAAAAAAAAAAABMS0AAAAAAAAAAAA=',
            '024932c9e90fe7864ee81ac34b896ebe7b1dc377f033b29e90adb3e78b003c5f'
        )        

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_invalid_htkn(self, mock_wallet):
        mock_wallet.return_value = {'asset': {}}
        with pytest.raises(web.HTTPBadRequest) as context:
            result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 10, 10, 0, 1, 'memo')

    @unittest_run_loop
    async def test_build_unsigned_transfer_with_target_not_created(self):
        with pytest.raises(web.HTTPNotFound):
            result = await build_unsigned_transfer('GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ', 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI', 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6', 0, 10, 0, 1, 'NotFound')

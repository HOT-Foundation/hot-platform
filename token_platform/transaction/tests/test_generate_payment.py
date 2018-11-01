import pytest
from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from asynctest import patch, call
from tests.test_utils import BaseTestClass

from stellar_base.transaction import Transaction
from stellar_base.transaction_envelope import TransactionEnvelope

from conf import settings
from transaction.generate_payment import get_signers, get_threshold_weight, generate_payment, build_unsigned_transfer
from transaction.transaction import get_transaction_by_memo
from wallet.tests.factory.wallet import StellarWallet
from router import reverse
from decimal import Decimal


class TestGetUnsignedTransaction(BaseTestClass):
    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet')
    @patch('transaction.generate_payment.get_stellar_wallet')
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request(self, mock_generate_payment, mock_stellar_wallet, mock_address):
        mock_generate_payment.return_value = {}
        balances = [{'balance': '9.9999200', 'asset_type': 'native'}]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'

        instance = mock_stellar_wallet.return_value
        instance.sequence = 5

        data = {
            'target_address': destination_address,
            'transaction_source_address': transaction_source_address,
            'amount_xlm': 10,
            'amount_htkn': 5,
        }
        url = reverse('generate-payment', wallet_address=source_address)
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 200
        mock_generate_payment.assert_called_once_with(
            transaction_source_address, source_address, destination_address, 5, 10, None, 5, None
        )
        mock_stellar_wallet.assert_called_once()

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet')
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request_with_invalid_target(self, mock_generate_payment, mock_address):
        mock_generate_payment.return_value = {}
        balances = [{'balance': '9.9999200', 'asset_type': 'native'}]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'

        data = {
            'target_address': 'invalid',
            'transaction_source_address': transaction_source_address,
            'amount_xlm': 10,
            'amount_htkn': 5,
            'sequence_number': 3,
        }
        url = reverse('generate-payment', wallet_address=source_address)
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        mock_generate_payment.assert_not_called()

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet')
    @patch('transaction.generate_payment.generate_payment')
    async def test_get_transaction_from_request_with_invalid_memo_on(self, mock_generate_payment, mock_address):
        mock_generate_payment.return_value = {}
        balances = [{'balance': '9.9999200', 'asset_type': 'native'}]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'

        data = {
            'target_address': 'invalid',
            'transaction_source_address': transaction_source_address,
            'amount_xlm': 10,
            'amount_htkn': 5,
            'memo_on': 'a',
            'sequence_number': 3,
        }
        url = reverse('generate-payment', wallet_address=source_address)
        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 400
        mock_generate_payment.assert_not_called()

    @unittest_run_loop
    @patch('transaction.generate_payment.get_transaction_by_memo')
    @patch('transaction.generate_payment.get_wallet')
    async def test_get_transaction_from_request_already_submitted(self, mock_address, mock_transaction_by_memo):
        balances = [{'balance': '9.9999200', 'asset_type': 'native'}]
        mock_address.return_value = StellarWallet(balances)
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        destination_address = 'GBFAIH5WKAJQ77NG6BZG7TGVGXHPX4SQLIJ7BENJMCVCZSUZPSISCLU5'
        memo = 'testmemo'

        data = {
            'target_address': destination_address,
            'transaction_source_address': transaction_source_address,
            'amount_xlm': 10,
            'amount_htkn': 5,
            'memo': memo,
            'sequence_number': 3,
        }
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

        data = {
            'target_address': destination_address,
            'transaction_source_address': transaction_source_address,
            'amount_htkn': 10,
        }
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
        mock_get_signer.return_value = [
            {"public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI", "weight": 1}
        ]
        mock_build.return_value = ('xdr', 'tx_hash')

        result = await generate_payment(
            'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
            'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
            'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6',
            '100',
            '0',
            None,
            None,
            None,
        )

        expect_data = {
            "@id": reverse(
                'generate-payment', wallet_address='GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
            ),
            "@transaction_url": reverse('transaction', transaction_hash='tx_hash'),
            "min_signer": 1,
            "signers": [{"public_key": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI", "weight": 1}],
            "xdr": "xdr",
            "transaction_hash": "tx_hash",
        }
        assert result == expect_data

    @unittest_run_loop
    @patch('transaction.generate_payment.Builder')
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_memo(self, mock_wallet, mock_builder):
        mock_wallet.return_value = {'asset': {settings['ASSET_CODE']: 10}}

        instance = mock_builder.return_value
        instance.gen_xdr.return_value = b'test-xdr'
        instance.te.hash_meta.return_value = b'test-xdr'

        amount_hot = 10
        amount_xlm = 0
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'

        result = await build_unsigned_transfer(
            transaction_source_address='GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
            source_address='GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
            destination_address=destination_address,
            amount_htkn=amount_hot,
            amount_xlm=amount_xlm,
            tax_amount_htkn=0,
            sequence=1,
            memo_text='memo',
        )
        mock_builder.assert_called_once()
        instance.gen_xdr.assert_called_once()
        instance.te.hash_meta.assert_called_once()
        instance.append_payment_op.assert_called_once_with(
            destination_address,
            amount_hot,
            asset_code=settings['ASSET_CODE'],
            asset_issuer=settings['ISSUER'],
            source=source_address,
        )
        instance.add_text_memo.assert_called_once()

    @unittest_run_loop
    @patch('transaction.generate_payment.Builder')
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_xlm_amount(self, mock_wallet, mock_builder):
        mock_wallet.return_value = {'asset': {}}

        instance = mock_builder.return_value
        instance.gen_xdr.return_value = b'test-xdr'
        instance.te.hash_meta.return_value = b'test-xdr'

        amount_hot = 0
        amount_xlm = 10
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'

        result = await build_unsigned_transfer(
            transaction_source_address='GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
            source_address=source_address,
            destination_address=destination_address,
            amount_htkn=amount_hot,
            amount_xlm=amount_xlm,
            tax_amount_htkn=0,
            sequence=1,
            memo_text='memo',
        )

        mock_builder.assert_called_once()
        instance.gen_xdr.assert_called_once()
        instance.te.hash_meta.assert_called_once()
        instance.append_payment_op.assert_called_once_with(destination_address, amount_xlm, source=source_address)
        instance.add_text_memo.assert_called_once()

    @unittest_run_loop
    @patch('transaction.generate_payment.Builder')
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_xlm_and_htkn_amount_with_trust(self, mock_wallet, mock_builder):
        mock_wallet.return_value = {'asset': {settings['ASSET_CODE']: 10}}

        instance = mock_builder.return_value
        instance.gen_xdr.return_value = b'test-xdr'
        instance.te.hash_meta.return_value = b'test-xdr'

        amount_hot = 10
        amount_xlm = 10
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'

        result = await build_unsigned_transfer(
            transaction_source_address='GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
            source_address=source_address,
            destination_address=destination_address,
            amount_htkn=amount_hot,
            amount_xlm=amount_xlm,
            tax_amount_htkn=0,
            sequence=1,
            memo_text='memo',
        )

        mock_builder.assert_called_once()
        instance.gen_xdr.assert_called_once()
        instance.te.hash_meta.assert_called_once()
        calls = [
            call.append_payment_op(
                destination_address,
                amount_hot,
                asset_code=settings['ASSET_CODE'],
                asset_issuer=settings['ISSUER'],
                source=source_address,
            ),
            call.append_payment_op(destination_address, amount_xlm, source=source_address),
        ]
        instance.assert_has_calls(calls, any_order=True)
        instance.add_text_memo.assert_called_once()

    @unittest_run_loop
    @patch('transaction.generate_payment.Builder')
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_usigned_transfer_with_tax_amount(self, mock_wallet, mock_builder):
        mock_wallet.return_value = {'asset': {settings['ASSET_CODE']: 10}}

        instance = mock_builder.return_value
        instance.gen_xdr.return_value = b'test-xdr'
        instance.te.hash_meta.return_value = b'test-xdr'

        amount_hot = 10
        amount_xlm = 10
        destination_address = 'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6'
        source_address = 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI'
        tax_amount_htkn = 2

        result = await build_unsigned_transfer(
            transaction_source_address='GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
            source_address=source_address,
            destination_address=destination_address,
            amount_htkn=amount_hot,
            amount_xlm=amount_xlm,
            tax_amount_htkn=tax_amount_htkn,
            sequence=1,
            memo_text='memo',
        )

        mock_builder.assert_called_once()
        instance.gen_xdr.assert_called_once()
        instance.te.hash_meta.assert_called_once()
        calls = [
            call.append_payment_op(
                destination_address,
                amount_hot,
                asset_code=settings['ASSET_CODE'],
                asset_issuer=settings['ISSUER'],
                source=source_address,
            ),
            call.append_payment_op(destination_address, amount_xlm, source=source_address),
            call.append_payment_op(
                settings['TAX_COLLECTOR_ADDRESS'],
                tax_amount_htkn,
                asset_code=settings['ASSET_CODE'],
                asset_issuer=settings['ISSUER'],
                source=source_address,
            ),
        ]
        instance.assert_has_calls(calls, any_order=True)
        instance.add_text_memo.assert_called_once()

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_invalid_htkn(self, mock_wallet):
        mock_wallet.return_value = {'asset': {}}
        with pytest.raises(web.HTTPBadRequest) as context:
            result = await build_unsigned_transfer(
                'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
                'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6',
                10,
                10,
                0,
                1,
                'memo',
            )

    @unittest_run_loop
    @patch('transaction.generate_payment.get_wallet_detail')
    async def test_build_unsigned_transfer_with_target_not_created(self, mock_wallet):
        mock_wallet.side_effect = web.HTTPNotFound()
        with pytest.raises(web.HTTPNotFound):
            result = await build_unsigned_transfer(
                'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ',
                'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'GDMZSRU6XQ3MKEO3YVQNACUEKBDT6G75I27CTBIBKXMVY74BDTS3CSA6',
                0,
                10,
                0,
                1,
                'NotFound',
            )


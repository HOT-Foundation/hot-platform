from tests.test_utils import BaseTestClass
from aiohttp.test_utils import unittest_run_loop
from wallet.get_current_tx_sequence import get_current_tx_sequence_from_request
from asynctest import patch
from router import reverse
# from aiohttp.web_exceptions import HTTPBadRequest

class TestGetcurrentTransactionNumber(BaseTestClass):

    @unittest_run_loop
    @patch('wallet.get_current_tx_sequence.get_current_sequence_number')
    async def test_get_current_tx_sequence_from_request_success(self, mock_seq_no) -> None:
        mock_seq_no.return_value = 12314355345345
        wallet_address = 'GASF2Q2GZMQMMNSYDU34MU4GJKSZPSN7FYKQEMNH4QJMVE3JR3C3I3N5'
        url = reverse('current-sequence', wallet_address=wallet_address)

        resp = await self.client.request("GET", url)
        assert resp.status == 200

        message = await resp.json()
        seq_number = message.get('current_sequence', )
        assert isinstance(seq_number, int)
        mock_seq_no.assert_called_once_with('GASF2Q2GZMQMMNSYDU34MU4GJKSZPSN7FYKQEMNH4QJMVE3JR3C3I3N5')


    @unittest_run_loop
    @patch('wallet.get_current_tx_sequence.get_current_sequence_number')
    async def test_get_current_tx_sequence_not_found(self, mock_seq_no) -> None:
        mock_seq_no.return_value = None
        wallet_address = 'test'
        url = reverse('current-sequence', wallet_address=wallet_address)

        resp = await self.client.request("GET", url)
        assert resp.status == 404

        message = await resp.json()
        expect = f"Not found current sequence of wallet address \'{wallet_address}\', Please ensure wallet address is valid."
        assert message['error'] == expect

        mock_seq_no.assert_called_once_with('test')
